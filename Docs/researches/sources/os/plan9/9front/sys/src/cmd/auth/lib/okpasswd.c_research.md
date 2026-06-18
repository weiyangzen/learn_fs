# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/okpasswd.c

Basic password policy checker.

Key responsibilities:
- Trims trailing spaces from a password copy.
- Requires at least eight characters.
- Rejects trivial strings such as `login`, `guest`, `passwd`, `anonymous`, and their reverses.

Dependencies:
- Used by `getpass` when password policy checking is requested.
