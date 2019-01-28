# coding: utf-8
# This file is a part of the RedSpri Simple Python Messaging Oriented Middleware
# Server Module

import socket
import threading
import time
import RSPMoMPacket as Packet


# noinspection PyShadowingNames
class ServerSettings:

    def __init__(self,
                 serverPort: int = 25566, serverHost: str = "0.0.0.0", serverBackLogMax: int = 10,
                 serverBufferSize: int = 2048, serverAddressFamily: int = socket.AF_INET,
                 serverSocketType: int = socket.SOCK_STREAM, serverProtocolNumber: int = 0,
                 serverEncoding: str = "utf-8"):
        self.__serverPort: int = serverPort
        self.__serverHost: str = serverHost
        self.__serverBackLogMax: int = serverBackLogMax
        self.__serverBufferSize: int = serverBufferSize
        self.__serverAddressFamily: int = serverAddressFamily
        self.__serverSocketType: int = serverSocketType
        self.__serverProtocolNumber: int = serverProtocolNumber
        self.__serverEncoding: str = serverEncoding

    def getServerPort(self) -> int:
        return self.__serverPort

    def getServerHost(self) -> str:
        return self.__serverHost

    def getServerBackLogMax(self) -> int:
        return self.__serverBackLogMax

    def getServerBufferSize(self) -> int:
        return self.__serverBufferSize

    def getServerAddressFamily(self) -> int:
        return self.__serverAddressFamily

    def getServerSocketType(self) -> int:
        return self.__serverSocketType

    def getServerProtocolNumber(self) -> int:
        return self.__serverProtocolNumber

    def getServerEncoding(self) -> str:
        return self.__serverEncoding


class Server:

    def __init__(self, settings: ServerSettings = ServerSettings()):
        self.__socketRunning: bool = False
        self.__serverSettings: ServerSettings = settings
        self.__clients: list[ClientThread] = list()

    def getSettings(self) -> ServerSettings:
        return self.__serverSettings

    def sendPacket(self, packet: Packet) -> None:
        for client in self.__clients:
            if client.is_alive():
                client.sendPacket(packet)

    def stop(self) -> None:
        self.__socketRunning = False

    def start(self) -> None:
        print("[RESPMoM] Server Starting...")
        time.sleep(1)
        self.__socketRunning = True
        print("[RESPMoM] Server Context 0/2")
        serverSocket = socket.socket(self.__serverSettings.getServerAddressFamily(),
                                     self.__serverSettings.getServerSocketType(),
                                     self.__serverSettings.getServerProtocolNumber())
        print("[RESPMoM] Server Context 1/2")
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[RESPMoM] Server Context 2/2")
        print("[RESPMoM] Server will bind on " + str(self.__serverSettings.getServerHost()) + ":" +
              str(self.__serverSettings.getServerPort()))
        serverSocket.bind((self.__serverSettings.getServerHost(), self.__serverSettings.getServerPort()))
        print("[RESPMoM] Server bound successfully!")
        time.sleep(1)
        while self.__socketRunning:
            try:
                serverSocket.listen(self.__serverSettings.getServerBackLogMax())
                print("[RESPMoM] Server started and listening!")
                newClient = serverSocket.accept()
                print("[RESPMoM] Client accepted...")
                (clientSocket, clientAddress) = newClient
                (clientIp, clientPort) = clientAddress
                clientThread = ClientThread(clientIp, clientPort, clientSocket, self)
                print("[RESPMoM] Client thread created!")
                clientThread.start()
                self.__clients.append(clientThread)
            except socket.timeout:
                pass
        print("[RESPMoM] Server Stopping...")
        time.sleep(1)
        serverSocket.close()
        self.__socketRunning = False
        print("[RESPMoM] Server Stopped.")


class ClientThread(threading.Thread):

    def __init__(self, clientIp: str, clientPort: int, clientSocket: socket, serverSocket: Server):
        threading.Thread.__init__(self)
        self.__clientIp: str = clientIp
        self.__clientPort: int = clientPort
        self.__clientSocket: socket = clientSocket
        self.__serverSocket: Server = serverSocket
        print("[RESPMoM] New client thread for " + str(self.__clientIp) + ":" + str(self.__clientPort))

    def sendPacket(self, clientPacket: Packet) -> None:
        packet = Packet.serialize(clientPacket)
        print("[RESPMoM] Client " + str(self.__clientIp) + ":" + str(self.__clientPort) +
              " >> rooting >> (leaving) packet " + packet)
        self.__clientSocket.send(
            packet.encode(self.__serverSocket.getSettings().getServerEncoding()))
        print("[RESPMoM] Client " + str(self.__clientIp) + ":" + str(self.__clientPort) +
              " << rooted << (leaving) packet.")

    def run(self):
        print("[RESPMoM] Client " + str(self.__clientIp) + ":" + str(self.__clientPort) + " connected!")
        time.sleep(1)
        loop: bool = True
        while loop:
            try:
                clientPacket = self.__clientSocket.recv(self.__serverSocket.getSettings().getServerBufferSize()).\
                    decode(self.__serverSocket.getSettings().getServerEncoding())
                if not clientPacket:
                    break
                packet = Packet.deserialize(clientPacket)
                if packet.getPacketIdentifier() == "__RSPMOM_Quit":
                    loop = False
                else:
                    print("[RESPMoM] Client " + str(self.__clientIp) + ":" + str(self.__clientPort) +
                          " << rooting << (joining) packet " + clientPacket)
                    self.__serverSocket.sendPacket(packet)
                    print("[RESPMoM] Client " + str(self.__clientIp) + ":" + str(self.__clientPort) +
                          " << rooted << (joining) packet.")
            except ConnectionResetError:
                loop = False
        print("[RESPMoM] Client " + str(self.__clientIp) + ":" + str(self.__clientPort) + " disconnected!")
