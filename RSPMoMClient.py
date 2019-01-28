# coding: utf-8
# This file is a part of the RedSpri Simple Python Messaging Oriented Middleware
# Client Module

import socket
import time
import RSPMoMPacket as Packet
import threading


# noinspection PyShadowingNames
class ClientSettings:

    def __init__(self,
                 serverPort: int = 25566, serverHost: str = "0.0.0.0", serverBufferSize: int = 2048,
                 serverAddressFamily: int = socket.AF_INET, serverSocketType: int = socket.SOCK_STREAM,
                 serverEncoding: str = "utf-8"):
        self.__serverPort: int = serverPort
        self.__serverHost: str = serverHost
        self.__serverBufferSize: int = serverBufferSize
        self.__serverAddressFamily: int = serverAddressFamily
        self.__serverSocketType: int = serverSocketType
        self.__serverEncoding: str = serverEncoding

    def getServerPort(self) -> int:
        return self.__serverPort

    def getServerHost(self) -> str:
        return self.__serverHost

    def getServerBufferSize(self) -> int:
        return self.__serverBufferSize

    def getServerAddressFamily(self) -> int:
        return self.__serverAddressFamily

    def getServerSocketType(self) -> int:
        return self.__serverSocketType

    def getServerEncoding(self) -> str:
        return self.__serverEncoding


class Client:

    def __init__(self, packetReceiveAction = None, settings: ClientSettings = ClientSettings()):
        self.__socketRunning: bool = False
        self.__socket: socket = None
        self.__packetReceiveAction = packetReceiveAction
        self.__clientSettings: ClientSettings = settings

    def getSettings(self) -> ClientSettings:
        return self.__clientSettings

    def start(self) -> None:
        try:
            print("[RESPMoM] Client Starting...")
            time.sleep(1)
            self.__socketRunning = True
            print("[RESPMoM] Client Context 0/2")
            clientSocket = socket.socket(self.__clientSettings.getServerAddressFamily(),
                                         self.__clientSettings.getServerSocketType())
            print("[RESPMoM] Client Context 1/2")
            serverAddress = (self.__clientSettings.getServerHost(), self.__clientSettings.getServerPort())
            print("[RESPMoM] Client Context 2/2")
            print("[RESPMoM] Client will connect on " + str(self.__clientSettings.getServerHost()) + ":" +
                  str(self.__clientSettings.getServerPort()))
            clientSocket.connect(serverAddress)
            print("[RESPMoM] Client connected successfully!")
            self.__socket = clientSocket
            threading.Thread(None, self.__work).start()
        except socket.error as exc:
            print("[RESPMoM] Error during client starting:" + str(exc))
            self.__socketRunning = False

    def sendPacket(self, clientPacket: Packet = Packet.Packet("unknown")) -> None:
        print("[RESPMoM] Sending packet...")
        time.sleep(1)
        if self.__socketRunning:
            packet = Packet.serialize(clientPacket)
            print("[RESPMoM] Packet info: " + packet)
            self.__socket.send(packet.encode(self.__clientSettings.getServerEncoding()))
            print("[RESPMoM] Packet sent")
        else:
            print("[RESPMoM] Error: Client not running!")

    def __work(self):
        while self.__socketRunning:
            packet = self.__receivePacket()
            if packet is not None:
                self.__packetReceiveAction(packet)

    def __receivePacket(self) -> Packet:
        print("[RESPMoM] Receiving packet...")
        time.sleep(1)
        try:
            serverPacket = self.__socket.recv(self.__clientSettings.getServerBufferSize()).\
                decode(self.__clientSettings.getServerEncoding())
            if not serverPacket:
                return None
            else:
                print("[RESPMoM] Packet info: " + serverPacket)
                packet = Packet.deserialize(serverPacket)
                print("[RESPMoM] Packet received")
            return packet
        except ConnectionAbortedError:
            pass

    def stop(self) -> None:
        time.sleep(1)
        print("[RESPMoM] Sending Close...")
        self.sendPacket(Packet.Packet("__RSPMOM_Quit"))
        time.sleep(1)
        print("[RESPMoM] Client Stopping...")
        self.__socket.close()
        self.__socketRunning = False
        print("[RESPMoM] Client Stopped.")
