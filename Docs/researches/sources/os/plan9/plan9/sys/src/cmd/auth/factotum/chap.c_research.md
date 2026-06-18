# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/chap.c

Factotum protocol implementation for CHAP and MS-CHAP.

Key points:
- Client role receives a binary challenge, finds a password key, and computes CHAP or MS-CHAP response structures.
- Server role gets a challenge from the auth server, passes it to the peer, collects user and response, and forwards the response to the auth server.
- Validates returned ticket/authenticator and exposes optional MS-CHAP secret bytes in `AuthInfo`.
- Implements local helpers for MD5 CHAP, LM response, NT response, and DES block hashing.

Dependencies:
- Uses factotum protocol framework, auth server protocol, MD4/MD5, and DES block cipher helpers.

Notable behavior:
- LM response is zeroed for passwords longer than 14 characters to avoid the LM vulnerability and buffer overflow.
