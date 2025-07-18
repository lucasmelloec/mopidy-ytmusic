import os
import json
from pathlib import Path

from mopidy import commands

from mopidy_ytmusic import logger


class YTMusicCommand(commands.Command):
    def __init__(self):
        super().__init__()
        self.add_child("setup", SetupCommand())
        self.add_child("reauth", ReSetupCommand())


class SetupCommand(commands.Command):
    help = "Generate oauth.json"

    def run(self, args, config):
        from ytmusicapi.setup import setup_oauth

        filepath = input(
            "Enter the path where you want to save oauth.json [default=current dir]: "
        )
        if not filepath:
            filepath = os.getcwd()
        path = Path(filepath + "/oauth.json")
        print('Using "' + str(path) + '"')
        if path.exists():
            print("File already exists!")
            return 1

        credentials_path = Path(filepath + "/credentials.json")
        credentials = {}
        credentials["client_id"] = input("Enter your client_id: ")
        credentials["client_secret"] = input("Enter your client_secret: ")
        with open(credentials_path, "w") as file:
            json.dump(credentials, file)

        try:
            setup_oauth(client_id=credentials["client_id"], client_secret=credentials["client_secret"], filepath=str(path))
        except Exception:
            logger.exception("YTMusic setup failed")
            return 1
        print("Authentication JSON data saved to {}".format(str(path)))
        print("")
        print("Update your mopidy.conf to reflect the new auth file:")
        print("   [ytmusic]")
        print("   enabled=true")
        print("   oauth_json=" + str(path))
        print("   credentials_json=" + str(path))
        return 0


class ReSetupCommand(commands.Command):
    help = "Regenerate auth.json"

    def run(self, args, config):
        from ytmusicapi import setup_oauth

        path = config["ytmusic"]["oauth_json"]
        if not path:
            logger.error("oauth_json path not defined in config")
            return 1

        credentials_path = config["ytmusic"]["credentials_json"]
        if not credentials_path:
            logger.error("credentials_json path not defined in config")
            return 1
        with open(credentials_path, "r") as file:
            credentials = json.load(file)

        print('Updating credentials in  "' + str(path) + '"')
        print("Updating via oauth, follow the instructions from ytmusicapi")
        try:
            setup_oauth(client_id=credentials["client_id"], client_secret=credentials["client_secret"], filepath=path)
        except Exception:
            logger.exception("YTMusic setup failed")
            return 1
        print("Authentication JSON data saved to {}".format(str(path)))
        return 0
