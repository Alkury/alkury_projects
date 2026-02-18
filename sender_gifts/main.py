from pyrogram import Client, filters
import config
from bot_adder import read_json

app = Client(
    "alkury",
    api_id=config.api_id,
    api_hash=config.api_hash
)

@app.on_message(filters.private)
async def track_new_msg(client, message):
    me = await app.get_me()
    if me.id == message.from_user.id:
        if message.text:
            if message.text[0] == ".":
                print(message)
                msg = message.text[1:].split(" ")
                print(msg)
                if len(msg) == 2:
                    name = msg[0]
                    text_gift = " ".join(msg[1:])
                else:
                    name = msg[0]
                    text_gift = None
                json_file = await read_json("ids.json")
                json_file = json_file["gifts"]
                if name in json_file.keys():
                    if text_gift:
                        await client.send_gift(chat_id=message.chat.id, gift_id=int(json_file[name]), text=text_gift)
                    else:
                        await client.send_gift(chat_id=message.chat.id, gift_id=int(json_file[name]))


def main():
    app.run()


if __name__ == "__main__":
    main()