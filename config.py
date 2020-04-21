import json


class Config:
    def __init__(self):
        with open("config_secrets.json", encoding="UTF-8") as config_file:
            data = json.loads(config_file.read())
        if "vk_bot_key" not in data or "tg_bot_key" not in data:
            print("!!! Config secrets fields are not valid")
            raise KeyError
        self.vk_bot_key = data["vk_bot_key"]
        self.tg_bot_key = data["tg_bot_key"]

    def check(self):
        print(f"vk_bot_key: \"{self.vk_bot_key}\"")
        print(f"tg_bot_key: \"{self.tg_bot_key}\"")


if __name__ == '__main__':
    conf = Config()
    conf.check()
