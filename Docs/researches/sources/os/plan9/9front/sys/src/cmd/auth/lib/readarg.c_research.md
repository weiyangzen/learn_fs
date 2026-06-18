# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/readarg.c

Null-terminated argument reader.

Key responsibilities:
- Reads one byte at a time from an fd.
- Copies up to `len-1` bytes into the destination.
- Stops successfully at NUL and leaves the output NUL-terminated.
- Returns `-1` on EOF before NUL.

Dependencies:
- Used by simple auth service protocols such as guard.
