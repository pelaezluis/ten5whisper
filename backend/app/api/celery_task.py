from uuid import UUID
from app.core.worker import celery
import asyncio

# import translators as ts
from deep_translator import GoogleTranslator
from gtts import gTTS

from app.utils.utils import validate_format
from app.utils.fastapi_globals import g
from app.utils.storage_redis import add_prediction_to_redis


######################################## TRANSCRIBE AUDIO ##########################################
async def transcribe_audio_whisper(audio_media_path: str, job_id: UUID | str):
    """
    Transcribe voice message to text and storage it in the database
    """
    ext = audio_media_path.split(".")[-1]
    try:
        if validate_format(ext):
            data = await convert_audio_file(audio_media_path)
            print(data)
            await add_prediction_to_redis(job_id, data)
        else:
            print(f"*** INVALID FORMAT {ext}")
            return None

    except Exception as err:
        print(f"*** COULDN'T CONVERT {audio_media_path}")
        print("This was the error:", err)
        return None


async def convert_audio_file(audio_media_path: str):
    """
    Convert an opus audio to a wav audio for transcription
    """
    print(">>> This is the input: ", audio_media_path)
    result = g.whisper_model.transcribe(audio_media_path, fp16=False)
    transcription = result["text"]
    language_source = result["language"]
    language_target = "en" if language_source == "es" else "es"
    translator = GoogleTranslator(source=language_source, target=language_target)
    translation = translator.translate(transcription)
    audio_media_path_output = f'{audio_media_path.split(".")[0]}_translated.mp3'

    data = {
        "input": {
            "audio_media_path_in": audio_media_path,
            "transcription": transcription,
            "language_source": language_source,
        },
        "output": {
            "audio_media_path_out": audio_media_path_output,
            "translation": translation,
            "language_target": language_target,
        },
    }
    tts = gTTS(translation, lang=language_target)
    tts.save(audio_media_path_output)
    return data


@celery.task(name="transcribe_voice_message")
def transcribe_voice_message(audio_media_path: str, job_id: str | UUID):
    print("MODELS:", g.whisper_model)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        transcribe_audio_whisper(audio_media_path=audio_media_path, job_id=job_id)
    )
