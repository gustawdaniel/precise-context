import json
import os
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Configuration
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
PRODUCT_FILE = 'product.md'

import json
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Configuration
# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
PRODUCT_FILE = os.path.join(BASE_DIR, 'product.md')
ANALYSIS_VERSION = 2  # Increment this to force re-analysis of existing leads
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'leads_analyzed.jsonl')

# --- Pydantic Models for Structured Output ---

class LeadScores(BaseModel):
    role_fit: int = Field(..., description="0-100 score: How well their job title/function matches our target audience.")
    engagement: int = Field(..., description="0-100 score: How active and responsive they are in the conversation.")
    technical_needs: int = Field(..., description="0-100 score: How clear their need for technical/software solutions is.")

class QualitativeAnalysis(BaseModel):
    role_description: str = Field(..., description="Inferred job role/function based on context.")
    personality_profile: str = Field(..., description="Tone, communication style, patience, professionalism.")
    key_information: str = Field(..., description="Valuable data points shared (e.g., specific tech stack, budget, timeline, pain points).")

class LeadAnalysis(BaseModel):
    tags: List[str] = Field(..., description="List of 3-5 keywords characterizing the lead (e.g., 'Founder', 'Skeptical', 'High Budget', 'Urgent').")
    scores: LeadScores
    qualitative: QualitativeAnalysis
    reasoning: str = Field(..., description="Brief explanation of why these scores and tags were assigned.")
    engaging_reply: str = Field(..., description="A draft of a short, engaging, and personalized message to send to this lead.")

# --- Helper Functions ---

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {filepath}")
        return []

def normalize_phone(phone):
    if not phone:
        return None
    # Keep it simple: remove spaces, dashes, parens. 
    # If duplicates persist due to + prefix, consider keeping or removing it consistently.
    # Current behavior: +48 123 -> +48123
    return re.sub(r'[\s\-()]+', '', phone)

def load_product_description():
    try:
        with open(PRODUCT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Product description unavailable."

def consolidate_database() -> Dict[str, int]:
    """
    Reads the entire JSONL output, deduplicates by phone (last write wins),
    rewrites the file if duplicates were found, and returns the progress map.
    """
    if not os.path.exists(OUTPUT_FILE):
        return {}
    
    unique_data = {}
    total_lines = 0
    
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                total_lines += 1
                try:
                    data = json.loads(line)
                    phone = data.get('phone')
                    if phone:
                        # Overwrite with latest version
                        unique_data[phone] = data
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading database: {e}")
        return {}

    # Check for duplicates
    if len(unique_data) < total_lines:
        print(f"  -> Found {total_lines - len(unique_data)} duplicate entries. Consolidating database...")
        # Rewrite the file
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                for data in unique_data.values():
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            print("  -> Database consolidated successfully.")
        except Exception as e:
            print(f"  -> Error rewriting database: {e}")
    
    # Return progress map based on unique data
    progress = {}
    for phone, data in unique_data.items():
        progress[phone] = data.get('_analysis_version', 0)
        
    return progress

def save_result(result: Dict[str, Any]):
    """Appends a single result to the JSONL file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')

# --- Main Logic ---

def main():
    print(f"Starting Enhanced Lead Analysis (Version {ANALYSIS_VERSION})...")
    
    # Check for API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[ERROR] OPENAI_API_KEY environment variable is not set.")
        print("Please export your API key: export OPENAI_API_KEY='sk-...'")
        return

    # Initialize Agno Agent
    product_context = load_product_description()
    
    agent = Agent(
        model=OpenAIChat(id="gpt-4o"),
        description="You are an expert sales development representative (SDR) analyzer.",
        instructions=[
            f"You are analyzing leads for the following product:\n{product_context}",
            "Analyze the conversation history deeply.",
            "Determine the LeadScores objectively based on evidence.",
            "Extract QualitativeAnalysis to give a human-readable profile.",
            "Assign relevant Tags to help filter this lead later.",
            "Draft a reply that is casual, short, and relevant to the last message.",
            "Do not be generic."
        ],
        output_schema=LeadAnalysis,
    )

    # Load Data
    files = os.listdir(INPUT_DIR)
    member_files = [f for f in files if 'whatsAppMembers' in f and f.endswith('.json')]
    message_files = [f for f in files if 'whatsAppMessages' in f and f.endswith('.json')]
    
    if not member_files or not message_files:
        print("Missing input files in input/ directory.")
        return

    member_files.sort()
    message_files.sort()
    
    members_path = os.path.join(INPUT_DIR, member_files[-1])
    messages_path = os.path.join(INPUT_DIR, message_files[-1])
    
    members = load_json(members_path)
    messages = load_json(messages_path)
    
    print(f"Loaded {len(members)} members and {len(messages)} messages.")
    
    # Group messages
    msg_by_sender = {}
    for msg in messages:
        sender = msg.get('sender')
        if not sender: continue
        norm_sender = normalize_phone(sender)
        if norm_sender not in msg_by_sender:
            msg_by_sender[norm_sender] = []
        msg_by_sender[norm_sender].append(msg)
        
    # Load Progress
    progress_map = consolidate_database()
    
    # Prepare list to process
    to_process = []
    skipped_count = 0
    
    for member in members:
        phone = member.get('phoneNumber')
        norm_phone = normalize_phone(phone)
        
        # Check if already processed with current version
        if norm_phone in progress_map and progress_map[norm_phone] == ANALYSIS_VERSION:
            skipped_count += 1
            continue
            
        msgs = msg_by_sender.get(norm_phone, [])
        if not msgs:
            # Skip users with no messages? Or analyze them as "Inactive"? 
            # For now, let's skip empty conversations to save tokens.
            # actually, maybe they *received* messages? The scraper gets full chat.
            # If msg list is empty, we have no text to analyze.
            continue
            
        to_process.append((member, msgs))
        
    # Sort to prioritize most active (optional, but good for demo)
    to_process.sort(key=lambda x: len(x[1]), reverse=True)
    
    print(f"Skipped {skipped_count} already processed leads.")
    print(f"Queued {len(to_process)} leads for analysis.")
    print("-" * 50)
    
    for i, (member, msgs) in enumerate(to_process):
        name = member.get('name', 'Unknown')
        phone = member.get('phoneNumber')
        norm_phone = normalize_phone(phone)
        
        print(f"[{i+1}/{len(to_process)}] Analyzing {name} ({len(msgs)} msgs)...")
        
        # Context
        conversation_text = ""
        for m in msgs:
            sender = m.get('sender', 'Unknown')
            text = m.get('message', '')
            time = m.get('time', '')
            conversation_text += f"[{time}] {sender}: {text}\n"
            
        try:
            response = agent.run(f"Analyze this conversation:\n\n{conversation_text}")
            analysis = response.content
            
            # Construct Result Object
            analysis_data = {}
            if hasattr(analysis, 'model_dump'):
                 analysis_data = analysis.model_dump()
            elif isinstance(analysis, dict):
                 analysis_data = analysis
            else:
                 print(f"  -> Warning: Received unstructured response for {name}")
                 analysis_data = {"raw_content": str(analysis)}

            result = {
                "_analysis_version": ANALYSIS_VERSION,
                "processed_at": datetime.now().isoformat(),
                "name": name,
                "phone": norm_phone, # Use normalized as key ID
                "original_phone": phone,
                "original_data": member,
                "message_count": len(msgs),
                # Flatten analysis for easier JSONL reading if desired, or keep nested
                "analysis": analysis_data,
                # Store messages? Might bloat file. Let's store them for now as requested.
                "messages": msgs 
            }
            
            save_result(result)
            
            if hasattr(analysis, 'scores') and hasattr(analysis.scores, 'role_fit'):
                 print(f"  -> Done. Role: {analysis.qualitative.role_description} | Fit: {analysis.scores.role_fit}/100")
            else:
                 print(f"  -> Done (Unstructured). Saved raw response.")
            
        except Exception as e:
            print(f"  -> Error: {e}")
            import traceback
            traceback.print_exc()

    print("-" * 50)
    print(f"Analysis complete. Results in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
