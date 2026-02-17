# Precise Context: Conversation intelligence for messaging platforms

**Precise Context** is an advanced, end-to-end system designed to transform raw WhatsApp conversation history into actionable sales intelligence. It features a chrome extension for data extraction, an AI-powered analyzer for lead scoring, and a modern dashboard for visualization.

> **Works with WhatsApp**

![Screencast](branding_book/precise-context-whatsapp.gif)

## 🚀 Key Features

*   **Smart Extraction**: Chrome extension to securely export group chat members and messages from WhatsApp Web.
*   **AI Analysis**: Python-based agent (using `agno` & OpenAI GPT-4o) that scores leads on:
    *   **Role Fit**: Relevance of their job title/status.
    *   **Engagement**: Activity level and responsiveness.
    *   **Technical Needs**: Evidence of specific requirements.
*   **Qualitative Profiling**: Generates personality profiles and contextual summaries.
*   **Interactive Dashboard**: Nuxt 4 powered UI to browse, filter, and view analyzed leads.

---

## 📂 Repository Structure

*   `whatsapp-extension/`: **The Collector**. A Chrome extension to scrape data.
*   `lead-analyzer/`: **The Brain**. Python scripts to process JSON exports and generate AI insights.
*   `lead-dashboard/`: **The Interface**. A web application to visualize the analyzed data.

---

## 🛠️ Usage Guide

### Phase 1: Data Collection (Extension)

1.  Open Chrome and navigate to `chrome://extensions`.
2.  Enable **Developer Mode** (top right).
3.  Click **Load unpacked** and select the `whatsapp-extension` folder.
4.  Open WhatsApp Web and navigate to a target group chat.
5.  Click the extension icon to export:
    *   `whatsAppMembers.json`: Member details.
    *   `whatsAppMessages.json`: Chat history.

### Phase 2: Analysis (The Brain)

1.  Navigate to the analyzer directory:
    ```bash
    cd lead-analyzer
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Important**: Place your exported JSON files into `lead-analyzer/input/`.
    *   Rename the members file to `whatsAppMembers.json`.
    *   Ensure `whatsAppMessages.json` is present.
4.  Set your OpenAI API Key:
    ```bash
    export OPENAI_API_KEY='sk-...'
    ```
5.  Run the analyzer:
    ```bash
    python main.py
    ```
    *   *This will process the data and output results to `output/leads_analyzed.jsonl`.*

### Phase 3: Visualization (Dashboard)

1.  Navigate to the dashboard directory:
    ```bash
    cd lead-dashboard
    ```
2.  Install dependencies:
    ```bash
    pnpm install
    # or npm install
    ```
3.  Start the development server:
    ```bash
    pnpm dev
    ```
4.  Open your browser to `http://localhost:3000` to view your leads!

---

## 🔧 Prerequisites

*   **Python 3.12+**
*   **Node.js 18+**
*   **OpenAI API Key** (GPT-4o access recommended)

## 🛡️ Privacy & Security

*   Data is processed locally and sent to OpenAI API only for analysis.
*   No data is sent to third-party servers from the extension.
*   **Disclaimer**: This tool is for educational and legitimate business purposes only. Respect WhatsApp's Terms of Service and user privacy.

---

*Built with ❤️ by [Precise Lab](https://preciselab.space).*

![Logo](whatsapp-extension/images/precise_lab_logo.svg)
