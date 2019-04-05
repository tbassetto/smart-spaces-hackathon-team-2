from flask import Flask
from webexteamssdk import WebexTeamsAPI

app = Flask(__name__)
api = WebexTeamsAPI(access_token="NTlmNWZmYTgtNWNmZC00Mjk1LTk1ZTYtZWI2Yzk3ZWU2NWE4YjI1Njc3OGItYTc5_PF84_a1254c6e-117d-49ff-9197-dd52b439f69c")

ROOM_ID = "Y2lzY29zcGFyazovL3VzL1JPT00vYzNhNjBlZjAtNTVmMS0xMWU5LWEyMmItZDkxYWYwODhkZGJh"

@app.route('/emergency_contact/<string:name>')
def emergency_contact(name):
    api.messages.create(roomId=ROOM_ID,
                        markdown="Hey! **{}** is lost. Check the map and fetch him/her!".format(name),
                        files=["https://www.nmbu.no/sites/default/files/styles/nmbu_artikkel_hovedbilde/public/main_article_media/mazemap_utsnitt.jpg?itok=Yna50PnE"]
                        )
    return "success"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
