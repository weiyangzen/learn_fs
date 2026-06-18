# File Research: sources/os/plan9/plan9/sys/src/cmd/cat.c

Minimal Plan 9 `cat`. `cat(int f, char *s)` reads 8192-byte chunks from a file descriptor and writes them to stdout, aborting via `sysfatal` on read/write errors.

`main` reads stdin when no files are supplied; otherwise it opens each named file read-only, copies it, and closes it. It sets `argv0 = "cat"` for diagnostics.
