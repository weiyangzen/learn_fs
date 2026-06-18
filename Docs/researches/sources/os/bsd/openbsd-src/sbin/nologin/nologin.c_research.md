# File Research: sources/os/bsd/openbsd-src/sbin/nologin/nologin.c

Purpose: Minimal shell replacement for unavailable accounts. It prints `/etc/nologin.txt` if present, otherwise a default message, then exits with failure.

Behavior:
- Unveils `/etc/nologin.txt` read-only.
- Pledges `stdio rpath`.
- Opens `/etc/nologin.txt`; on failure writes `This account is currently not available.\n` to stdout.
- If opened, streams file contents to stdout in `BUFSIZ` chunks.
- Always exits with status 1.

Notes:
- Defines `_PATH_NOLOGIN_TXT` separately from `_PATH_NOLOGIN`.
- Does not parse arguments or inspect environment.
