# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_getuserpasswd.c

This file obtains username/password credentials through factotum-style auth RPC.

Key behavior:
- `auth_getuserpasswd` starts an RPC with formatted parameters, repeatedly handles RPC phases, and returns `UserPasswd`.
- Internal `dorpc` sends one verb/value pair and invokes `getkey` when the RPC asks for keys.

Important details:
- Copies `user` and `password` attributes out of the returned RPC data.
- Handles `ARneedkey` by calling the supplied key-acquisition callback.
