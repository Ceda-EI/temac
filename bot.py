from telethon import TelegramClient, events
from matrix_client.client import MatrixClient
import config
import os
import magic
import logging

logging.basicConfig(level=logging.ERROR)


def media_uploader(path, matrix_bot):
    mime = magic.from_file(path, mime=True)
    with open(path, 'rb') as f:
        mxc = matrix_bot.upload(f.read(), mime)
    return mxc, mime.split('/')[0]


async def send_to_matrix(event, room, matrix_bot):
    media = await event.download_media()
    if media is not None:
        paths = media.split("\n")
        mxcs = list(map(
            lambda x: media_uploader(x, matrix_bot),
            paths
        ))
        for (mxc, mime), path in zip(mxcs, paths):
            if mime == "image":
                room.send_image(mxc, path)
            elif mime == "audio":
                room.send_audio(mxc, path)
            elif mime == "video":
                room.send_video(mxc, path)
            else:
                room.send_file(mxc, path)
            os.remove(path)

    if event.raw_text != "":
        room.send_text(event.raw_text)


matrix_bot = MatrixClient(config.matrix_creds['server'])
matrix_bot.login(
    username=config.matrix_creds['username'],
    password=config.matrix_creds['password']
)
client = TelegramClient('Temec', config.api_id, config.api_hash).start()
rooms = matrix_bot.get_rooms()

for chan_id, room_id in config.mappings:
    client.add_event_handler(
        lambda x: send_to_matrix(x, rooms[room_id], matrix_bot),
        events.NewMessage(chats=[chan_id])
    )

print("Started listening")
client.run_until_disconnected()
