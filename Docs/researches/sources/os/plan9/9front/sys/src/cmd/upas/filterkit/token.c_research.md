# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/token.c

This command creates or validates short time-window HMAC tokens.

Key behavior:
- Usage: `token key [tokenfile]`.
- With one arg, prints a 5-character base64 prefix of HMAC-SHA1 over a normalized current ctime string.
- The time string has the HH:MM:SS field replaced with colons, making tokens day-granular.
- With two args, reads a file and checks for tokens generated for today and the prior 13 days.
- Exits nil on match/create, `no match` otherwise.

Integration and risks:
- Token space is short by design; suitable only for low-stakes filtering workflows.
