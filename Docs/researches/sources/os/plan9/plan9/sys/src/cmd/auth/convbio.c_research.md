# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/convbio.c

Converts old account bio records to pipe-delimited format.

Key points:
- `ordbio` parses one legacy bio line into username, name, department, and up to 10 email addresses.
- `nwrbio` writes `user|user|name|dept|email...`.
- Main streams stdin to stdout.

Dependencies:
- Uses `Acctbio` from `authcmdlib.h`.

Notable behavior:
- Email addresses are extracted from `<...>` spans.
