# File Research: sources/os/plan9/9front/sys/src/cmd/du.c

This is Plan 9 `du`, a disk-usage walker with options for all files, byte counts, qids, access/modify times, autoscaling, quiet warnings, and a read-through mode.

Key responsibilities:
- Parses flags `-aefhnqstu`, block size `-b`, and SI prefix output scale `-p`.
- Recursively walks directories with `dirread`.
- Rounds file lengths to a configured block size with `blkmultiple`.
- Prints totals or per-file values using integer, floating, or autoscaled output.
- Avoids directory cycles with a small qid/type/dev cache in `seen`.
- Optional `-r` reads every block of every file into `readbuf`.

Important implementation notes:
- `dirval` switches reported value between size, qid path, mtime, or atime.
- `dufile` builds child paths with Plan 9 `String`.
- `readflg` suppresses printing and turns traversal into an I/O read test.
- Warnings are suppressed by `-f`.
