from telethon import TelegramClient, events
from matrix_client.client import MatrixClient
import config


async def send_to_matrix(event, room):
    room.send_text(event.raw_text)


matrix_bot = MatrixClient(config.matrix_creds['server'])
matrix_bot.login(
    username=config.matrix_creds['username'],
    password=config.matrix_creds['password']
)
client = TelegramClient('Temec', config.api_id, config.api_hash).start()
rooms = matrix_bot.get_rooms()

for chan_id, room_id in config.mappings:
    client.add_event_handler(lambda x: send_to_matrix(x, rooms[room_id]),
                             events.NewMessage(chats=[chan_id]))


client.run_until_disconnected()
