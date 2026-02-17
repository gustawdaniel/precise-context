import json
import os
import random

# This script is only for presentation purposes. It replaces real names and phone numbers with fake ones.

INPUT_FILE = 'output/leads_analyzed.jsonl'
TEMP_FILE = 'output/leads_analyzed_anon.jsonl'

POLISH_FIRST_NAMES = [
    "Adam", "Adrian", "Agata", "Agnieszka", "Aleksandra", "Andrzej", "Anna", "Arkadiusz", "Artur", "Barbara",
    "Bartosz", "Beata", "Błażej", "Bogdan", "Borys", "Cezary", "Czesław", "Damian", "Daniel", "Daria",
    "Dariusz", "Dawid", "Dominik", "Dorota", "Ewa", "Ewelina", "Filip", "Gabriela", "Grzegorz", "Halina",
    "Hanna", "Hubert", "Iga", "Igor", "Iwona", "Izabela", "Jacek", "Jakub", "Jan", "Janusz",
    "Jarosław", "Jerzy", "Joanna", "Jolanta", "Julia", "Justyna", "Kacper", "Kamil", "Kamila", "Karol",
    "Karolina", "Katarzyna", "Kazimierz", "Kinga", "Klaudia", "Krzysztof", "Krystyna", "Leszek", "Łukasz", "Maciej",
    "Magdalena", "Małgorzata", "Marcin", "Marek", "Maria", "Mariola", "Mariusz", "Marta", "Mateusz", "Michał",
    "Mirosław", "Monika", "Natalia", "Mikołaj", "Oliwia", "Patrycja", "Patryk", "Paweł", "Piotr", "Przemysław",
    "Radosław", "Rafał", "Robert", "Sebastian", "Stanisław", "Stefan", "Szymon", "Tadeusz", "Tomasz", "Urszula",
    "Weronika", "Wiesław", "Wiktor", "Wojciech", "Zbigniew", "Zofia", "Zuzanna"
]

POLISH_LAST_NAMES = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak",
    "Dąbrowski", "Kozłowski", "Jankowski", "Mazur", "Wojciechowski", "Kwiatkowski", "Krawczyk", "Kaczmarek", "Piotrowski", "Grabowski",
    "Zając", "Pawłowski", "Michalski", "Król", "Wieczorek", "Jabłoński", "Wróbel", "Nowakowski", "Majewski", "Olszewski",
    "Stępień", "Malinowski", "Jaworski", "Adamczyk", "Dudek", "Nowicki", "Pawlak", "Górski", "Sikora", "Walczak",
    "Rutkowski", "Michalak", "Szewczyk", "Ostrowski", "Tomaszewski", "Pietrzak", "Zalewski", "Wróblewski", "Marciniak", "Jasiński",
    "Zawadzki", "Bąk", "Jakubowski", "Sadowski", "Duda", "Włodarczyk", "Wilk", "Chmielewski", "Borkowski", "Sokołowski"
]

def generate_fake_name():
    return f"{random.choice(POLISH_FIRST_NAMES)} {random.choice(POLISH_LAST_NAMES)}"

def anonymize():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    # Seed random for reproducibility within the run, though across runs names will change unless fixed seed
    random.seed(42) 

    with open(INPUT_FILE, 'r', encoding='utf-8') as f_in, \
         open(TEMP_FILE, 'w', encoding='utf-8') as f_out:
        
        user_counter = 1
        phone_map = {}
        name_map = {}

        for line in f_in:
            if not line.strip():
                continue

            data = json.loads(line)
            
            # Original PII (might be already anonymized "User N" or original names if file wasn't overwritten)
            original_phone = data.get('phone')
            original_name = data.get('name')

            # Generate fake PII if not already mapped
            if original_phone and original_phone not in phone_map:
                # Keep the same logic for phone numbers but ensure it handles if already anonymized
                # If it starts with +48600... it might be already anonymized, but we can't be sure easily.
                # Let's just generate a deterministically unique one based on counter
                fake_phone_number = f"+48{600000000 + user_counter}"
                phone_map[original_phone] = fake_phone_number
            
            if original_name and original_name not in name_map:
                fake_name = generate_fake_name()
                # Ensure uniqueness of full name if possible, though mostly statistical
                while fake_name in name_map.values():
                     fake_name = generate_fake_name()
                
                name_map[original_name] = fake_name
                
                # Simple split mapping not needed for "User N" inputs, but good to have if running on raw data
                # For "User 1", split is "User" and "1". Not useful to map "User" to "Adam".
                # We will skip part mapping to avoid "User" -> "Adam" global replace issues.
                
                user_counter += 1

            fake_phone = phone_map.get(original_phone, original_phone)
            fake_name = name_map.get(original_name, original_name)
            
            # Anonymize Root Fields
            data['name'] = fake_name
            data['phone'] = fake_phone
            
            # 'original_phone' might hold the REAL original phone if we are reprocessing raw data, 
            # OR it holds the anonymized phone from previous run.
            # If we want to be safe, we replace it too.
            if 'original_phone' in data:
                 data['original_phone'] = phone_map.get(data.get('original_phone'), fake_phone)

            # Anonymize original_data
            if 'original_data' in data:
                od = data['original_data']
                if 'phoneNumber' in od:
                    od['phoneNumber'] = phone_map.get(od.get('phoneNumber'), fake_phone)
                if 'profileId' in od:
                     od['profileId'] = phone_map.get(od.get('profileId'), fake_phone)
                if '_pk' in od:
                     od['_pk'] = phone_map.get(od.get('_pk'), fake_phone)
                if 'name' in od:
                    od['name'] = fake_name

            # Anonymize Messages
            if 'messages' in data:
                for msg in data['messages']:
                    # Replace sender phone
                    sender = msg.get('sender')
                    for p_orig, p_fake in phone_map.items():
                        if p_orig in str(sender):
                             msg['sender'] = msg['sender'].replace(p_orig, p_fake)
                        if p_orig in str(msg.get('_pk', '')):
                             msg['_pk'] = msg['_pk'].replace(p_orig, p_fake)
            
            # Anonymize Analysis Text
            def clean_text(text):
                if not text: return text
                t = text
                if original_name:
                    t = t.replace(original_name, fake_name)
                    # Handle "Firstname" replacement if original was "Firstname Lastname"
                    # If original is "User 1", split[0] is "User". replacing "User" is bad.
                    parts = original_name.split()
                    if len(parts) > 0 and parts[0] != "User": 
                         if len(parts[0]) > 2:
                             t = t.replace(parts[0], fake_name.split()[0])
                return t

            if 'analysis' in data:
                if 'engaging_reply' in data['analysis']:
                    data['analysis']['engaging_reply'] = clean_text(data['analysis']['engaging_reply'])
                if 'reasoning' in data['analysis']:
                    data['analysis']['reasoning'] = clean_text(data['analysis']['reasoning'])
                if 'qualitative' in data['analysis']:
                    # Also clean qualitative fields as they might contain names
                    for k, v in data['analysis']['qualitative'].items():
                        data['analysis']['qualitative'][k] = clean_text(v)


            f_out.write(json.dumps(data, ensure_ascii=False) + '\n')

    # Replace original file
    os.replace(TEMP_FILE, INPUT_FILE)
    print(f"Anonymization complete. Processed {user_counter-1} users.")

if __name__ == "__main__":
    anonymize()
