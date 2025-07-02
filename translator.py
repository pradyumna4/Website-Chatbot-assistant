import os
from deep_translator import GoogleTranslator

# Translate text using deep-translator
# This function is now a no-op to enforce English-only output

def translate(text, lang_from, lang_to):
    # If translation is needed, use GoogleTranslator
    if lang_from == lang_to or lang_from == 'en':
        return text
    try:
        lang_map = {
            'en': 'english',
            'hi': 'hindi',
            'ta': 'tamil',
            'ml': 'malayalam',
            'kn': 'kannada',
        }
        src = lang_map.get(lang_from, lang_from)
        tgt = lang_map.get(lang_to, lang_to)
        result = GoogleTranslator(source=src, target=tgt).translate(text)
        return result
    except Exception as e:
        return f"[Translation Error] {str(e)}"
