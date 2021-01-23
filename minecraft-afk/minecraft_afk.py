import time
import signal
import sys
from pathlib import Path
import yaml

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound


def read_config():
    path = Path(__file__).parent.parent.absolute().joinpath("config.yml")
    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print("Configuration file missing! Is it possible you've deleted it?")


def main():
    config = read_config()

    # split port and host
    match = re.match(r"((?P<host>[^\[\]:]+)|\[(?P<addr>[^\[\]]+)\])"
                     r"(:(?P<port>\d+))?$", config.server)
    if match is None:
        raise ValueError(f"Invalid server address: '{config.server}'")
    address = match.group("host") or match.group("addr")
    port = int(match.group("port") or 25565)

    auth_token = authentication.AuthenticationToken()
    try:
        auth_token.authenticate(config.username, config.password)
    except YggdrasilError as e:
        print(e)
        sys.exit()
    print(f"Authenticated successfully as {auth_token.username}")
    connection = Connection(
        address, port, auth_token=auth_token)

    def handle_goodbye(signum, frame):
        print("Signing out!")
        payload = {'username': config.username,
                   'password': config.password}
        try:
            authentication._make_request(authentication.AUTH_SERVER, "signout", payload)
        except:
            print("Failed to sign out with Yggdrasil")

    def handle_disconnect():
        print("Disconnected from server")
        if config.reconnect == True:
            connection.connect()
        else:
            sys.exit()

    connection.register_packet_listener(
        lambda packet: print(f"Connected to {address}!"), clientbound.play.JoinGamePacket)

    connection.register_packet_listener(
        handle_disconnect, clientbound.login.DisconnectPacket)

    try:
        connection.connect()
    except:
        print("Failed to connect to specified server")
        sys.exit()

    signal.signal(signal.SIGINT, handle_goodbye)
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
