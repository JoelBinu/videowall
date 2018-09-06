import logging

from .networking import NetworkingServer
from .networking.message_definition import ServerBroadcastMessage
from .media_manager import MediaManagerServer
from .player import PlayerServer

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, player_platform, media_path, base_time_offset, ip, server_broadcast_port, server_clock_port,
                 client_broadcast_port, client_config_dict):
        self._networking = NetworkingServer(server_broadcast_port, client_broadcast_port)
        self._player = PlayerServer(player_platform, ip, server_clock_port)
        self._base_time_offset = base_time_offset
        self._client_config_dict = client_config_dict
        self._media_manager = MediaManagerServer(media_path)

    def get_media_filenames(self):
        return self._media_manager.get_filenames()

    def play(self, filename):
        self._player.play(self._media_manager.get_full_path(filename), self._base_time_offset)
        self._networking.send_broadcast(ServerBroadcastMessage(
            filename=filename,
            base_time=self._player.get_base_time(),
            ip=self._player.get_ip(),
            clock_port=self._player.get_port(),
            client_config={ip: cfg for ip, cfg in self._client_config_dict.iteritems()}
        ))

    def is_playing(self):
        return self._player.is_playing()

    def close(self):
        self._networking.close()
        self._player.close()

    def get_duration_seconds(self):
        return self._player.get_duration_seconds()

    def get_position_seconds(self):
        return self._player.get_position_seconds()

    def get_clients(self):
        return self._networking.get_clients()

    def sync_media(self, remote_paths):
        self._media_manager.sync(remote_paths)
