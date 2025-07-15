import asyncio
from dosui import DOSBotUI
from doschatbot import DOSBot

if __name__ == "__main__":
    dosbot = DOSBot()
    dosbot.db_init()
    asyncio.run(dosbot.run())

    dosui = DOSBotUI()
    dosui.run()