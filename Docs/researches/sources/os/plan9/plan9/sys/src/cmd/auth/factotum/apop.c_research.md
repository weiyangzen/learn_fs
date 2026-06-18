# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/apop.c

Factotum protocol implementation for APOP and CRAM-MD5.

Key points:
- Implements both client and server roles through phase states.
- Client role receives a challenge, finds a key with `!password`, computes MD5 or HMAC-MD5 response, and returns it.
- Server role obtains a challenge from the auth server, sends it to the peer, receives user/response, and forwards validation to the auth server.
- On success, validates returned ticket/authenticator and fills `AuthInfo`.

Dependencies:
- Uses factotum `Proto`, `Fsstate`, key lookup, Plan 9 auth server ticket protocol, and `libsec` MD5/HMAC.

Notable behavior:
- APOP uses `MD5(challenge || password)`, while CRAM uses HMAC-MD5.
