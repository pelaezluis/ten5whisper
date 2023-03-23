from app.core.worker import celery
import asyncio
from fastapi import Depends
from app.core.config import settings
import json
import httpx

from backend.app.core.deps import s3_auth
# import whisper

######################################## TRANSCRIBE AUDIO ##########################################
async def transcribe_audio(audio_media_id: str): #, s3=s3_auth()):
    """
    Transcribe voice message to text and storage it in the database
    """
    async with SessionLocal() as session:
        media_audio = await crud.audio.get(id=audio_media_id, db_session=session)
        if media_audio is None:
            print("Id Audio error")
            return None
        if media_audio.media_id is None:
            print("Audio register has not media object")
            return None

        name_file = media_audio.media.path.split("/")[-1]
        media_path = media_audio.media.path
        ext = name_file.split(".")[-1]
        ext = ext.split("?")[0]

        print(f"This is the media path {media_path}")
        try:
            if validate_format(ext):
                temp_in = tempfile.NamedTemporaryFile(suffix=f".{ext}")
                with open(temp_in.name, "wb") as audio_file_temp:
                    s3.download_fileobj(
                        settings.BUCKET_NAME, media_path, audio_file_temp
                    )
                    print(">>> AUDIO DOWNLOADED")
                    audio = await convert_audio_file(audio_file_temp.name, ext)

                    c = 0  # This is to do a while loop if fails at first try

                    while audio == None and c < 10:
                        audio = await convert_audio_file(audio_file_temp.name, ext)
                        c += 1
                        print(f">>> TRY {c}")
                    if audio:

                        async with httpx.AsyncClient() as client:
                            headers: dict = {
                                "authorization": f"Bearer {settings.BASE_TOKEN}",
                                "Content-Type": f"audio/wav",
                                "Transfer-encoding": "chunked",
                            }

                            res = await client.post(
                                settings.API_WIT_AI_ENDPOINT,
                                headers=headers,
                                data=audio,
                            )
                            res = res.content.decode("utf-8").replace("\r", ",")

                            if res[-1] == "\n":
                                res = res[:-2]
                            res = "[" + res + "]"

                            res_format = json.loads(res)
                            final_text = ""

                            for complete_text in res_format:
                                if "is_final" in complete_text:
                                    final_text += f" {complete_text['text']}"

                            print('-'*30)
                            final_text = final_text.lstrip()
                            data = {"text": final_text}
                            

                        obj_new = {"voice_transcription": data["text"], "sentiment": sentiment['data']['text']}
                        await crud.audio.update(
                            obj_current=media_audio, obj_new=obj_new, db_session=session
                        )
                        
                        print(f">>> AUDIO {media_audio.id} TRANSCRIBED")
                        data['id'] = audio_media_id
                        data['audio_in'] = media_path
                        data['sentiment'] = sentiment['data']['text']
                        return data
                    else:
                        obj_new = {
                            "voice_transcription": "This transcription is not available"
                        }
                        await crud.audio.update(
                            obj_current=media_audio, obj_new=obj_new, db_session=session
                        )
                        print(
                            f"*** COULDN'T CONVERT {media_audio.id} - {media_audio.media.path}"
                        )
                        return None
            else:
                print(f"*** INVALID FORMAT {ext}")
                return None

        except Exception as err:
            obj_new = {"voice_transcription": "This transcription is not available"}
            await crud.audio.update(
                obj_current=media_audio, obj_new=obj_new, db_session=session
            )
            print(f"*** COULDN'T CONVERT {media_audio.id} - {media_audio.media.path}")
            print("This was the error:", err)
            return None


async def transcribe_audio_whisper(audio_media_id: str, s3=s3_auth()):
    """
    Transcribe voice message to text and storage it in the database
    """
    async with SessionLocal() as session:
        media_audio = await crud.audio.get(id=audio_media_id, db_session=session)
        if media_audio is None:
            print("Id Audio error")
            return None
        if media_audio.media_id is None:
            print("Audio register has not media object")
            return None

        name_file = media_audio.media.path.split("/")[-1]
        media_path = media_audio.media.path
        ext = name_file.split(".")[-1]
        ext = ext.split("?")[0]

        print(f"This is the media path {media_path}")
        try:
            if validate_format(ext):
                temp_in = tempfile.NamedTemporaryFile(suffix=f".{ext}")
                with open(temp_in.name, "wb") as audio_file_temp:
                    s3.download_fileobj(
                        settings.BUCKET_NAME, media_path, audio_file_temp
                    )
                    print(">>> AUDIO DOWNLOADED")
                    data = await convert_audio_file(
                        audio_file_temp.name, ext, returned=0
                    )
                    c = 0  # This is to do a while loop if fails at first try

                    while data == None and c < 10:
                        data = await convert_audio_file(
                            audio_file_temp.name, ext, returned=0
                        )
                        c += 1
                        print(f">>> TRY {c}")
                    if data:
                        obj_new = {"voice_transcription": data["text"]}

                        await crud.audio.update(
                            obj_current=media_audio, obj_new=obj_new, db_session=session
                        )
                        print(f">>> AUDIO {media_audio.id} TRANSCRIBED")
                        return data
                    else:
                        obj_new = {
                            "voice_transcription": "This transcription is not available"
                        }
                        await crud.audio.update(
                            obj_current=media_audio, obj_new=obj_new, db_session=session
                        )
                        print(
                            f"*** COULDN'T CONVERT {media_audio.id} - {media_audio.media.path}"
                        )
                        return None
            else:
                print(f"*** INVALID FORMAT {ext}")
                return None

        except Exception as err:
            obj_new = {"voice_transcription": "This transcription is not available"}
            await crud.audio.update(
                obj_current=media_audio, obj_new=obj_new, db_session=session
            )
            print(f"*** COULDN'T CONVERT {media_audio.id} - {media_audio.media.path}")
            print("This was the error:", err)
            return None


async def convert_audio_file(
    path_audio_media: str,
    input_format: str,
    output_format: str = "wav",
    returned: int = 1,
):
    """
    Convert an opus audio to a wav audio for transcription
    """
    print(">>> This is the input: ", path_audio_media)

    AudioSegment.converter = which("ffmpeg")
    try:
        if input_format == "opus":
            audio_data = BytesIO(read_audio(path_audio_media))
            sound = AudioSegment.from_file(audio_data, codec=input_format)
        else:
            sound = AudioSegment.from_file(path_audio_media)

        audio_output_temp = tempfile.NamedTemporaryFile(suffix=f".{output_format}")
        sound.set_frame_rate(48000)
        sound.export(audio_output_temp.name, format=output_format)

        if returned == 1:
            with open(audio_output_temp.name, "rb") as audio_output:
                audio = audio_output.read()
            print(">>> AUDIO CONVERTED")
            return audio
        elif returned == 0:
            model = whisper.load_model("base")
            result = model.transcribe(audio_output_temp.name)
            print(">>> AUDIO CONVERTED")
            return result
    except Exception as err:
        # print("!!! ERROR:",err, "FORMAT: ", input_format)
        print("!!! ERROR FORMAT: ", input_format)
        return None


@celery.task(name="transcribe_voice_message")
def transcribe_voice_message(audio_media_id: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(transcribe_audio(audio_media_id=audio_media_id))

