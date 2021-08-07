import os
import socket
from getpass import getpass
from paramiko import SSHClient, AutoAddPolicy, BadHostKeyException, AuthenticationException, SSHException

import cv2
import numpy as np


class Scp:

    def __init__(self, hostname: str, port: int = 22, username: str = None, password: str = None):
        """
        Scp implement by paramiko
        :param hostname: the server to connect
        :param port: the server port to connect
        :param username:
        :param password:
        """

        self._ssh = SSHClient()
        self._ssh.set_missing_host_key_policy(AutoAddPolicy())
        self._try_times = 0
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._sftp = None
        self._connected = False
        self.connect(hostname, port, username, password)

    def connect(self, hostname: str, port: int = 22, username: str = None, password: str = None):
        self._hostname = hostname
        self._port = port
        if username is None or password is None:
            while self._try_times < 3 and not self.connected():
                self._try_times += 1
                self._hostname = hostname
                self._port = port
                self._username = input("Username: ")
                self._password = getpass("Password: ")
                self._connect()
        else:
            self._username = username
            self._password = password
            self._connect()

    def _connect(self):
        try:
            self._ssh.connect(self._hostname, self._port, self._username, self._password)
            self._sftp = self._ssh.open_sftp()
            self._connected = True
            self._try_times = 0
            print("scp is connected")
        except BadHostKeyException as e:
            print(e)
        except AuthenticationException as e:
            print(e)
        except SSHException as e:
            print(e)
        except socket.error as e:
            print(e)

    def connected(self):
        return self._connected

    @property
    def hostname(self):
        return self._hostname

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    def __call__(self, path: str):
        pass

    def get(self, remote_path: str, local_path: str):
        if self._sftp is not None:
            if os.path.isdir(local_path):
                local_path = os.path.join(local_path, os.path.basename(remote_path))
            self._sftp.get(remote_path, local_path)

    def get_image(self, path: str, flag=cv2.IMREAD_COLOR):

        if self._sftp is not None:
            data = self._sftp.open(path).read()
            return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flag)
        else:
            print("scp is disconnected")
            return None
