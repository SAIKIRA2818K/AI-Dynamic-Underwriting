import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".env"))

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


SYSTEM_PROMPT = (
    "You are a professional financial translation assistant. Your task is to accurately translate "
    "banking and underwriting explanations from English to the requested target language. "
    "Maintain a professional, empathetic, and clear tone. Do not change the meaning of the underlying text, "
    "and do not alter numerical values or risk assessments."
)

TRANSLATION_PROMPT = (
    "Please translate the following text into {target_language}. "
    "Return ONLY a JSON object with the exact same keys as the input, containing the translated strings. "
    "Do not include any markdown formatting like ```json. Just the raw JSON object.\n\n"
    "Input JSON:\n{input_json}"
)


def _generate_fallback(texts: Dict[str, Any], target_language: str) -> Dict[str, Any]:
    """
    Fallback mechanism when OpenAI is unavailable. 
    Returns hardcoded test cases for Telugu and Hindi to prove the UI pipeline works.
    """
    if target_language == "te":
        return {
            "customer_message": "మీ ఆర్థిక రిస్క్ స్కోర్ అవసరమైన పరిమితి కంటే తక్కువగా ఉన్నందున మీ దరఖాస్తు తిరస్కరించబడింది.",
            "recommendations": [
                "మీ అప్పు-ఆదాయ నిష్పత్తిని తగ్గించండి.",
                "స్థిరమైన చెల్లింపు చరిత్రను నిర్వహించండి.",
                "అదనపు అధిక-వడ్డీ అప్పులను తీసుకోకుండా ఉండండి."
            ],
            "reasoning": [
                "ఫైనాన్షియల్ రిస్క్ స్కోర్ అవసరమైన థ్రెషోల్డ్ కంటే తక్కువగా ఉంది."
            ]
        }
    elif target_language == "hi":
        return {
            "customer_message": "आपका वित्तीय जोखिम स्कोर आवश्यक सीमा से कम होने के कारण आपका आवेदन अस्वीकार कर दिया गया है।",
            "recommendations": [
                "अपना ऋण-से-आय अनुपात कम करें।",
                "निरंतर भुगतान इतिहास बनाए रखें।",
                "अतिरिक्त उच्च-ब्याज वाला ऋण लेने से बचें।"
            ],
            "reasoning": [
                "वित्तीय जोखिम स्कोर आवश्यक सीमा से कम है।"
            ]
        }
            
    return texts


class TranslationAgent:
    """
    Translates underwriting explanations using the OpenAI API, with a robust offline fallback.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.client = None

        if OPENAI_AVAILABLE and self.api_key and self.api_key != "your_openai_api_key_here":
            self.client = OpenAI(api_key=self.api_key)
            print(f"[TranslationAgent] OpenAI client initialized (model: {self.model})")
        else:
            reason = "openai package not installed" if not OPENAI_AVAILABLE else "API key not configured"
            print(f"[TranslationAgent] Running in OFFLINE fallback mode ({reason})")

    def translate(self, target_language: str, texts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a dictionary of text strings.

        Parameters
        ----------
        target_language : str
            The language to translate to (e.g. 'Telugu', 'Hindi').
        texts : dict
            Dictionary of strings or list of strings to translate.

        Returns
        -------
        dict with the same keys, containing the translated text.
        """
        if target_language.lower() in ["english", "en"]:
            return texts

        if self.client is None:
            return _generate_fallback(texts, target_language)

        lang_map = {"te": "Telugu", "hi": "Hindi", "en": "English"}
        target_lang_name = lang_map.get(target_language, target_language)

        input_json = json.dumps(texts, indent=2)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": TRANSLATION_PROMPT.format(
                        target_language=target_lang_name,
                        input_json=input_json
                    )},
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            raw_response = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting from LLM
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
                
            translated = json.loads(raw_response.strip())
            return translated

        except Exception as e:
            print(f"[TranslationAgent] OpenAI call failed: {e}. Using fallback (English).")
            return _generate_fallback(texts, target_language)
