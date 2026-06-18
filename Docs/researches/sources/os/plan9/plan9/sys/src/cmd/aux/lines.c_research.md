# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/lines.c

This file copies complete newline-terminated lines from files or stdin to stdout.

Key behavior:
- Reads with `Brdline`.
- Writes each complete line as read.
- Processes stdin when no filenames are supplied.
- Opens and copies each named file otherwise.

Important details:
- Partial final lines without newline are not emitted by this implementation.
- Reports write and open errors with `sysfatal`.

Filesystem relevance:
- Indirect simple file utility.
