import time
import asyncio
import uuid
import sqlite3
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelChatMessageEvent, ChatMessageBadge, ChannelBitsUseEvent, ChannelPointsCustomRewardRedemptionData

def get_env_data_as_dict(path: str) -> dict:
    try:
        with open(path, 'r') as f:
            return dict(tuple(line.replace('\n', '').split('=')) for line
                in f.readlines() if not line.startswith('#'))
    except: 
        print("You need to include the .env file, John, with the APP_ID=<appid> and APP_SECRET=<secret>(don't show others this! its your bot!)")

async def user_refresh(token: str, refresh_token: str):
    print(f'my new user token is: {token}')

async def app_refresh(token: str):
    print(f'my new app token is: {token}')

# https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage
async def on_message(data: ChannelChatMessageEvent):
    message = data.event.message.text.split() 
    badges: ChatMessageBadge = data.event.badges

    allow_mods = get_env_data_as_dict('.env')["ALLOW_MODS"] or False
    command_prefix = get_env_data_as_dict('.env')["CMD_PREFIX"] or '!vr'

    if(len(message) >=2 and message[0] == command_prefix):
        for badge in badges:
            if((badge.set_id == "moderator" and allow_mods) or badge.set_id == "broadcaster"):
                add_item(username=data.event.chatter_user_name, link=message[1], method="VIDR")
    
# https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelbitsuse
async def on_bits(data: ChannelBitsUseEvent):
    bit_amount = get_env_data_as_dict('.env')["BIT_AMOUNT"] or 25
    message = data.event.message.text.split()
    
    if(data.event.bits == 25):
        add_item(username=data.event.chatter_user_name, link=message[0], method="BITS")

# https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchannel_points_custom_reward_redemptionadd
async def on_channelpointredemption(data: ChannelPointsCustomRewardRedemptionData):
    message = data.event.message.text.split()
    point_amount = get_env_data_as_dict('.env')["POINT_AMOUNT"] or 2500

    if(data.event.reward.cost == point_amount):
        add_item(username=data.event.chatter_user_name, link=message[0], method="GBOI")

async def run():
    # Set scope for claim
    USER_SCOPE=[AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.USER_READ_CHAT]
    
    # set up twitch api instance and add user authentication with some scopes
    print("Attempting to authenticate as bot ID " + get_env_data_as_dict('.env')["APP_ID"])
    twitch = await Twitch(get_env_data_as_dict('.env')["APP_ID"], get_env_data_as_dict('.env')["APP_SECRET"])
    
    auth = UserAuthenticator(twitch, USER_SCOPE, force_verify=False)
    print("Being redirected to Twitch.tv to authorize bot to access channel as your twitch user account")
    # User authorization 
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    user = await first(twitch.get_users())
    print("Creating websockets and subbing to channel for notifs")
    # Create websocket
    ws = EventSubWebsocket(twitch)
    eventsub = EventSubWebsocket(twitch)
    eventsub.start()
    print("Bot initialized and listening.")
    await eventsub.listen_channel_bits_use(user.id, on_bits)
    await eventsub.listen_channel_points_automatic_reward_redemption_add_v2(user.id, on_channelpointredemption)
    await eventsub.listen_channel_chat_message(user.id, user.id, on_message)

def add_item(username: str, link: str, method: str):
    #this will be for a stateful queue,  going to likely use sqlite3
    item={"uuid":str(uuid.uuid4()),"username":username,"link":link,"method":method,"etime":time.time()}
    print(item["uuid"], item["username"] + '|' + item["method"] + '|' + item["link"] + '|' + time.strftime("%I:%M:%S", time.localtime(item["etime"])))

    if(item["link"][:23] == "https://www.youtube.com" or item["link"][:19] == "https://youtube.com"):
        # webbrowser.open(item["link"], 2, autoraise=False)  #adventures in browser window opening, a no go :(
        connection = sqlite3.connect('queue.db')
        cursor = connection.cursor()

        cursor.execute(f"""
                       INSERT INTO queue VALUES 
                       ('{item['username']}', '{item['link']}', '{item['method']}', {item['etime']})
                       """)
        connection.commit()
        connection.close()
    else:
        print("Link invalid! Didn't goto youtube.com or was a youtube short or something")

def remove_item(id: int):
    connection = sqlite3.connect('queue.db')
    cursor = connection.cursor()
    full_queue = cursor.execute(f"""
                                DELETE FROM queue WHERE rowid = {id}
                                """)
    connection.commit()
    connection.close()

def read_queue():
    connection = sqlite3.connect('queue.db')
    cursor = connection.cursor()
    full_queue = cursor.execute(f"""
                                SELECT rowid, link, username, method, time FROM queue ORDER BY rowid ASC
                                """)
    return full_queue #this is temporary, need to return a data structure for populating a table, rather than the SQL connection object.  Will want to close before return

def clean_queue():
    connection = sqlite3.connect('queue.db')
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS queue (username TEXT, link TEXT, method TEXT, time REAL)")
    cursor.execute(f"""
                    DELETE FROM queue
                    WHERE time < strftime('%s', 'now', '-{get_env_data_as_dict('.env')["KEEP_HISTORY_HRS"]} hours');
                    """)
    print(f"DB: {cursor.rowcount} ROWS AFFECTED")
    connection.commit()
    connection.close()


def main():
    clean_queue()
    asyncio.run(run())

if __name__ == "__main__":
    main()