# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/error.c

Shared fatal error helper for auth commands.

Key responsibilities:
- Formats `argv0: ...` messages with varargs.
- Writes the message to stderr.
- Exits with the formatted error buffer.

Dependencies:
- Used by many auth command helper routines and tools.
