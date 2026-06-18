# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/httpauth.c

This file implements HTTP-style password checking against Plan 9 auth tickets.

Key behavior:
- `httpauth` dials the auth server, requests a ticket for the named user, derives a key from the supplied password, and decrypts/validates the ticket.

Important details:
- Returns success/failure rather than an `AuthInfo`.
- Not listed in `libauth/Makefile`, so it may be unused in this drawterm build.
