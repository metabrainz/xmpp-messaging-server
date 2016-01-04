#!/usr/bin/env python
"""
This is an external authentication script for Prosody.

Additional documentation:
* http://modules.prosody.im/mod_auth_external.html
* https://prosody.im/doc/authentication
"""
import sys


def from_prosody():
    input_data = sys.stdin.readline()
    if input_data:
        return input_data.split(":")
    else:
        return


def to_prosody(success):
    if success:
        print("1")
    else:
        print("0")
    sys.stdout.flush()


def auth(username, server, password):
    return True


def is_user(username, server):
    return True


while True:
    data = from_prosody()
    success = False
    if data and len(data) > 0:
        if data[0] == "auth":
            success = auth(data[1], data[2], data[3])
        elif data[0] == "isuser":
            success = is_user(data[1], data[2])
    to_prosody(success)
