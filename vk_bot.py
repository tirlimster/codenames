from config import Config


class VkBot:
    SECRETS = Config()

    def __init__(self, events):
        print(f"starting vk_bot {'(with empty key)' if self.SECRETS.vk_bot_key == 'empty_key' else ''}")
        pass

    def main_loop(self):
        pass
