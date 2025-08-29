from deep_translator import GoogleTranslator

class Translator:
    """
    Simple translator wrapper using deep_translator.GoogleTranslator.
    Default: Vietnamese ('vi') -> English ('en').
    """

    def __init__(self, source='vi', target='en'):
        self.translator = GoogleTranslator(source=source, target=target)

    def __call__(self, text):
        if not text:
            return ""
        try:
            return self.translator.translate(text)
        except Exception as e:
            raise RuntimeError(f"Translation failed: {e}") from e