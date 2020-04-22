import time
from database import Database
from vk_bot import VkBot
db = Database()


class Request:
    def __init__(self):
        pass


class MainLoop:
    def __init__(self):
        events = []

        # starting vk_bot
        vkbot = VkBot()
        # starting tg_bot

        while True:
            if len(events) == 0:
                time.sleep(0.1)
                continue
            ...


if __name__ == '__main__':
    MainLoop()
