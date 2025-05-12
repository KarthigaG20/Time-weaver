import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from datetime import datetime, timedelta
import json
from dateutil import parser
import os

# Initialize timetable storage
TIMETABLE_FILE = "timetable.json"

def load_timetable():
    if os.path.exists(TIMETABLE_FILE):
        with open(TIMETABLE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_timetable(timetable):
    with open(TIMETABLE_FILE, "w") as f:
        json.dump(timetable, f)

def parse_time_natural_language(time_str):
    try:
        return parser.parse(time_str).strftime("%H:%M")
    except:
        return None

def extract_entities(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    
    entities = {
        "subject": "",
        "day": "",
        "time": "",
        "duration": ""
    }
    
    # Extract subject (noun phrases)
    nouns = [word for word, pos in tagged if pos.startswith('NN')]
    
    # Extract adjectives
    adjectives = [word for word, pos in tagged if pos.startswith('JJ')]
    
    # Combine nouns and adjectives
    entities["subject"] = " ".join(nouns + adjectives)
    
    # Extract day (proper nouns like Monday, Tuesday)
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for word, pos in tagged:
        if word.lower() in days:
            entities["day"] = word.lower()
    
    # Extract time (numbers + AM/PM)
    time_phrases = ["am", "pm", "morning", "evening", "at"]
    for i, (word, pos) in enumerate(tagged):
        if word.lower() in time_phrases or pos == 'CD':
            time_str = " ".join(tokens[i-1:i+2])
            parsed_time = parse_time_natural_language(time_str)
            if parsed_time:
                entities["time"] = parsed_time
    
    # Extract duration (e.g., "for 1 hour")
    for i, (word, pos) in enumerate(tagged):
        if word.lower() == "for" and i+2 < len(tagged):
            duration = f"{tagged[i+1][0]} {tagged[i+2][0]}"
            entities["duration"] = duration
    
    return entities

def add_event(timetable, day, time, duration, subject):
    if day not in timetable:
        timetable[day] = []
    
    # Check for conflicts
    new_start = datetime.strptime(time, "%H:%M")
    new_end = new_start + timedelta(hours=float(duration.split()[0]))
    
    for event in timetable[day]:
        event_start = datetime.strptime(event["time"], "%H:%M")
        event_end = event_start + timedelta(hours=float(event["duration"].split()[0]))
        
        if (new_start < event_end) and (new_end > event_start):
            return False, "Time conflict!"
    
    timetable[day].append({
        "subject": subject,
        "time": time,
        "duration": duration
    })
    save_timetable(timetable)
    return True, "Event added!"

def process_input(text):
    timetable = load_timetable()
    entities = extract_entities(text.lower())
    
    if not entities["day"] or not entities["time"]:
        return "❌ Error: Could not detect day/time."
    
    success, message = add_event(
        timetable,
        entities["day"],
        entities["time"],
        entities["duration"] or "1 hour",  # Default duration
        entities["subject"] or "Meeting"   # Default subject
    )
    
    if success:
        return f"✅ {message}\n\nUpdated Timetable:\n{json.dumps(timetable, indent=2)}"
    else:
        return f"❌ {message}"

def get_timetable():
    timetable = load_timetable()
    return json.dumps(timetable, indent=2) if timetable else "No events scheduled yet."