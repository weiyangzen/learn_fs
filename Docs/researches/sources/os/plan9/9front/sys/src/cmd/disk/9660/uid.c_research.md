# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/uid.c

Incomplete/sketch file for detecting user database format.

Key behavior:
- Contains comments describing `/adm/users` and `/etc/{passwd,group}` field formats.
- Defines `isnumber`.
- Contains a non-C pseudocode-like `sniff(Biobuf *b)` body with placeholders such as “read first line of file into p;” and references to `_plan9`/`_unix`.

Research notes:
- This file does not appear to be production-compilable as written.
- It may be a dormant design note or unfinished utility for uid/gid mapping.
