import json, boto3, os, random

translate = boto3.client("translate")

# Map human language names to ISO codes for Amazon Translate
LANG_MAP = {
    "english": "en", "en": "en",
    "hindi": "hi", "hi": "hi",
    "malayalam": "ml", "ml": "ml",
    "tamil": "ta", "ta": "ta",
    "arabic": "ar", "ar": "ar",
    "french": "fr", "fr": "fr",
    "german": "de", "de": "de"
}

# Tiny demo catalog; replace with DynamoDB or an API later
BOOKS = {
    "fantasy": ["The Hobbit", "The Name of the Wind", "Mistborn"],
    "mystery": ["Gone Girl", "The Girl with the Dragon Tattoo", "Big Little Lies"],
    "romance": ["The Hating Game", "Me Before You", "The Rosie Project"],
    "sci-fi": ["Dune", "Project Hail Mary", "Neuromancer"],
    "non-fiction": ["Sapiens", "Atomic Habits", "Educated"],
    "history": ["Team of Rivals", "Guns, Germs, and Steel", "The Silk Roads"],
    "self-help": ["Deep Work", "The Power of Habit", "Mindset"],
    "biography": ["Steve Jobs", "Becoming", "The Diary of a Young Girl"]
}

def get_slot_value(event, slot_name):
    # Lex V2 structure
    slots = event["sessionState"]["intent"].get("slots") or {}
    slot = slots.get(slot_name)
    if not slot:
        return None
    val = slot.get("value") or {}
    # Prefer interpretedValue if present
    return val.get("interpretedValue") or val.get("originalValue")

def close(intent_name, message):
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {"name": intent_name, "state": "Fulfilled"},
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }

def lambda_handler(event, context):
    intent_name = event["sessionState"]["intent"]["name"]

    genre = (get_slot_value(event, "Genre") or "").strip().lower()
    language_in = (get_slot_value(event, "TargetLanguage") or "English").strip().lower()

    # Default and cleaning
    if genre not in BOOKS:
        genre = "fantasy"

    # Pick 3 recs
    picks = BOOKS[genre][:3]
    english_text = f"Top {genre.title()} book picks: {', '.join(picks)}."

    # Map language to code; fallback to English
    code = LANG_MAP.get(language_in, "en")

    # Translate from auto-detected language into target
    if code != "en":
        res = translate.translate_text(
            Text=english_text,
            SourceLanguageCode="auto",
            TargetLanguageCode=code
        )
        reply = res["TranslatedText"]
    else:
        reply = english_text

    # Return to Lex
    return close(intent_name, reply)
