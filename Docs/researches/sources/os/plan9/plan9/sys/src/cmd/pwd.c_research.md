# File Research: sources/os/plan9/plan9/sys/src/cmd/pwd.c

Purpose: Prints the current working directory.

Key behavior:
- Calls `getwd` into a fixed 512-byte buffer.
- Prints the path on success.
- Prints `pwd: %r` and exits with `getwd` status on failure.

Dependencies and integration:
- Uses Plan 9 libc only.

Risks and notes:
- Fixed path buffer size.
- Minimal command with no options.
