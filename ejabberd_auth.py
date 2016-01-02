#!/usr/bin/env python
"""
This is an external authentication script for ejabberd.

Additional documentation:
* http://docs.ejabberd.im/admin/guide/configuration/#external-script
* https://www.ejabberd.im/files/doc/dev.html#htoc9
* https://www.ejabberd.im/extauth
"""

import struct
import sys


def from_ejabberd():
    input_length = sys.stdin.read(2)
    if len(input_length) != 2:
        return
    (size,) = struct.unpack(">h", input_length.encode("utf-8"))
    return sys.stdin.read(size).split(':')


def to_ejabberd(success):
    if success:
        answer = 1
    else:
        answer = 0
    token = struct.pack(">hh", 2, answer)
    sys.stdout.write(token.decode("utf-8"))
    sys.stdout.flush()


def auth(username, server, password):
    return True


def is_user(username, server):
    return True


def set_password(username, server, password):
    return True


while True:
    data = from_ejabberd()
    success = False
    if data:
        if data[0] == "auth":
            success = auth(data[1], data[2], data[3])
        elif data[0] == "isuser":
            success = is_user(data[1], data[2])
        elif data[0] == "setpass":
            success = set_password(data[1], data[2], data[3])
    to_ejabberd(success)
