import os
from deep_translator import GoogleTranslator

# Translate text using deep-translator
# This function is now a no-op to enforce English-only output

def translate(text, lang_from, lang_to):
    # If translation is needed, use GoogleTranslator
    if lang_from == lang_to or lang_from == 'en':
        return text
    try:
        # Use direct language codes that GoogleTranslator accepts
        result = GoogleTranslator(source=lang_from, target=lang_to).translate(text)
        return result
    except Exception as e:
        return f"[Translation Error] {str(e)}"
