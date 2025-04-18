import edge_tts
import asyncio
import playsound
languages = {
    "1": {"code": "en", "name": "English", "voice": "en-US-JennyNeural"},
    "2": {"code": "hi", "name": "Hindi", "voice": "hi-IN-SwaraNeural"},
    "3": {"code": "fr", "name": "French", "voice": "fr-FR-DeniseNeural"},
    "4": {"code": "de", "name": "German", "voice": "de-DE-Stefan-Male"}
}

async def text_to_speech(text: str, lang: str)->None:
    voice = None
    if lang == 'en':
        voice = languages["1"]['voice']
    elif lang == 'hindi':
        voice = languages["2"]['voice']
    elif lang == 'fr':
        voice = languages["3"]['voice']
    elif lang == 'german':
        voice = languages["4"]['voice']

    output_file = "response.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

    playsound.playsound(output_file)

    await asyncio.sleep(0.5)





