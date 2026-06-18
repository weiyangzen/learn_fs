# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_getnv.c

Read status: complete.

Purpose: standard implementation of `gp_getenv` using the C library `getenv`.

Main logic:
- Looks up `key` with `getenv`.
- If found and output buffer is large enough, copies value, sets required length including NUL, and returns `0`.
- If found but buffer is too small, sets required length and returns `-1`.
- If missing, stores an empty string when possible, sets length to `1`, and returns `1`.

Filesystem/storage relevance:
- Environment variables commonly affect Ghostscript file search paths, temporary directories, and platform configuration.

Notable behavior:
- Expects `*plen` to be the caller-provided buffer size on input and required/actual size on output.
