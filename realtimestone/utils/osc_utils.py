from pythonosc import udp_client


def init_client(ip="127.0.0.1", port=5555):
    return udp_client.SimpleUDPClient(ip, port)