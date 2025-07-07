import time
import asyncio
import webbrowser
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

    if(len(message) >=2 and message[0] == "!vr"):
        for badge in badges:
            if((badge.set_id == "moderator" and allow_mods) or badge.set_id == "broadcaster"):
                add_item(username=data.event.chatter_user_name, link=message[1], method="VIDR")
    
# https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelbitsuse
async def on_bits(data: ChannelBitsUseEvent):
    bit_amount = get_env_data_as_dict('.env')["BIT_AMOUNT"] or 25
    message = data.event.message.text.split()
    
    if(data.event.bits == 25 and message[:23] == "https://www.youtube.com"):
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

    print("Attempting to authenticate as bot ID" + get_env_data_as_dict('.env')["APP_ID"])
    # set up twitch api instance and add user authentication with some scopes
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
    print("Bot initialized and listening.  Test with a !vr link from a moderator or broadcaster")
    await eventsub.listen_channel_bits_use(user.id, on_bits)
    await eventsub.listen_channel_points_automatic_reward_redemption_add_v2(user.id, on_channelpointredemption)
    await eventsub.listen_channel_chat_message(user.id, user.id, on_message)

def add_item(username: str, link: str, method: str):
    #this will be for a stateful queue, currently just writing to file?
    item={"username":username, "link":link, "method": method, "etime": time.gmtime()}
    print(item["username"] + '|' + item["method"] + '|' + item["link"] + '|' + time.strftime("%I:%M:%S", item["etime"]))
    if(item["link"][:23] == "https://www.youtube.com" or item["link"][:19] == "https://youtube.com"):
        webbrowser.open(item["link"], 1, autoraise=False)
    else:
        print("Link invalid! Didn't goto youtube.com or was a youtube short or something")

def remove_item(linenum: int):
    print("remove line, based on username and time?")
    
def read_queue():
    print("going to read the queue here on startup")

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()

    