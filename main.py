import time
import asyncio
import webbrowser
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import ChatEvent, AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelChatMessageEvent, ChatMessageBadge
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

def get_env_data_as_dict(path: str) -> dict:
    with open(path, 'r') as f:
       return dict(tuple(line.replace('\n', '').split('=')) for line
                in f.readlines() if not line.startswith('#'))

async def user_refresh(token: str, refresh_token: str):
    print(f'my new user token is: {token}')

async def app_refresh(token: str):
    print(f'my new app token is: {token}')

# https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage
async def on_message(data: ChannelChatMessageEvent):
    message = data.event.message.text.split() 
    badges: ChatMessageBadge = data.event.badges

    if(len(message) >=2 and message[0] == "!vr"):
        for badge in badges:
            if(badge.set_id == "moderator" or badge.set_id == "broadcaster"):
                add_item(data.event.chatter_user_name, message[1])
                webbrowser.open(message[1], 0)
    
async def run():
    # Set scope for claim
    USER_SCOPE=[AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.USER_READ_CHAT]

    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(get_env_data_as_dict('.env')["APP_ID"], get_env_data_as_dict('.env')["APP_SECRET"])
    auth = UserAuthenticator(twitch, USER_SCOPE, force_verify=False)

    # User authorization 
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    user = await first(twitch.get_users())

    # Create websocket
    ws = EventSubWebsocket(twitch)
    eventsub = EventSubWebsocket(twitch)
    eventsub.start()

    # create subscription to events
    await eventsub.listen_channel_bits_use(user.id, on_message)
    await eventsub.listen_channel_points_automatic_reward_redemption_add_v2(user.id, on_message)
    await eventsub.listen_channel_chat_message(user.id, user.id, on_message)

    try:
        input('press ENTER to stop\\n')
    finally:
        #we close event subscription the twitch api client
        await eventsub.stop()
        await twitch.close()

def add_item(username: str, link: str):
    #this will be for a stateful queue, currently just writing to file?
    item={"username":username, "link":link, "etime": time.gmtime()}
    print(item["username"] + '|' + item["link"] + '|' + time.strftime("%I:%M:%S", item["etime"]))

def remove_item(linenum: int):
    print("remove line, based on username and time?")
    
def read_queue():
    print("going to read the queue here on startup")

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()

    