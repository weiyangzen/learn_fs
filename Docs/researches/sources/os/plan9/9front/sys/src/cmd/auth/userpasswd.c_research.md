# File Research: sources/os/plan9/9front/sys/src/cmd/auth/userpasswd.c

Simple wrapper around `auth_getuserpasswd`.

Important behavior:
- Usage: `auth/userpasswd [-n] fmt`.
- With default behavior, can prompt through `auth_getkey`; `-n` disables prompting.
- Calls `auth_getuserpasswd(noprompt ? nil : auth_getkey, "proto=pass %s", argv[0])`.
- Prints username and password on separate lines.

Security note:
- Emits plaintext password to stdout by design; intended as a utility in trusted contexts.
