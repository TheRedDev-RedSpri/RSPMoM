# coding: utf-8
# This file is a part of the RedSpri Simple Python Messaging Oriented Middleware
# Client Module

import json


class Packet:

    def __init__(self, packetIdentifier: str, packetEmitter: str = "unknown", packetData=None):
        if packetData is None:
            packetData = dict()
        self.__packetIdentifier: str = packetIdentifier
        self.__packetEmitter: str = packetEmitter
        self.__packetData: dict = packetData

    def getPacketIdentifier(self) -> str:
        return self.__packetIdentifier

    def getPacketEmitter(self) -> str:
        return self.__packetEmitter

    def getPacketData(self) -> dict:
        return self.__packetData

    def setData(self, key: str, value = None) -> None:
        self.__packetData[key] = value

    def getData(self, key: str):
        try:
            return self.__packetData[key]
        except KeyError:
            return None

    def delData(self, key: str) -> None:
        try:
            del self.__packetData[key]
        except KeyError:
            pass


def deserialize(serialized: str) -> Packet:
    array = json.loads(serialized)
    return Packet(array[0], array[1], array[2])


def serialize(packet: Packet) -> str:
    return json.dumps([packet.getPacketIdentifier(), packet.getPacketEmitter(), packet.getPacketData()])
