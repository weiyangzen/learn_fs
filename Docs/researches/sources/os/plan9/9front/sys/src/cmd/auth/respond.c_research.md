# File Research: sources/os/plan9/9front/sys/src/cmd/auth/respond.c

Small wrapper around `auth_respond`.

Key responsibilities:
- Accepts auth parameter string and challenge.
- Calls `auth_respond` with `auth_getkey`.
- Writes the response and newline to stdout.

Dependencies:
- Uses Plan 9 auth library key lookup and response generation.
