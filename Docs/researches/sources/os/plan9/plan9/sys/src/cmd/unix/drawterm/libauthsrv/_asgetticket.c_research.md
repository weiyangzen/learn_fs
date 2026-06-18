# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asgetticket.c

This file reads ticket and authenticator material from an auth-server fd.

Key behavior:
- `_asgetticket` reads a ticket reply buffer and a ticket buffer using fixed auth protocol sizes.

Important details:
- Returns `-1` if either fixed-size read fails.
