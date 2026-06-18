# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9cr.c

Implements text challenge/response protocols `p9cr` and `vnc`. Client protocol writes a challenge and reads a response; server protocol writes a user, reads a challenge, writes a response, then validates through the auth server.

`p9cr` uses DES password-derived response formatting for Plan 9 netkey-style challenges. `vnc` derives an 8-byte DES key from `!password` after reversing bits in each byte, then encrypts the VNC challenge.

Server-side `getchal` contacts the auth server with a `Ticketreq`, reads a challenge, and later validates the response by reading a ticket and authenticator. Bad first-use keys can be disabled. `vncaddkey` stores preprocessed key material in `Key.priv`.
