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
    """Reads request from ejabberd.

    Reads from stdin: AABBBBBBBBB.....

    A: 2 bytes of length data (a short in network byte order)
    B: a string of length found in A that contains operation in plain text operation are as follows:
        auth:User:Server:Password (check if a username/password pair is correct)
        isuser:User:Server (check if it's a valid user)
        setpass:User:Server:Password (set user's password)
        tryregister:User:Server:Password (try to register an account)
        removeuser:User:Server (remove this account)
        removeuser3:User:Server:Password (remove this account if the password is correct)
    """
    input_length = sys.stdin.read(2)
    if len(input_length) != 2:
        return
    (size,) = struct.unpack(">h", input_length.encode("utf-8"))
    return sys.stdin.read(size).split(':')


def to_ejabberd(success):
    """Sends result to ejabberd.

    AABB
    A: the number 2 (coded as a short, which is bytes length of following result)
    B: the result code (coded as a short), should be 1 for success/valid, or 0 for failure/invalid
    """
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


while True:
    data = from_ejabberd()
    success = False
    if data:
        if data[0] == "auth":
            success = auth(data[1], data[2], data[3])
        elif data[0] == "isuser":
            success = is_user(data[1], data[2])
    to_ejabberd(success)
