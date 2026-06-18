# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/error.c

Defines `error`, a shared fatal helper for auth commands. It prefixes messages with `argv0`, formats varargs into a stack buffer, writes to stderr, and exits with the same message buffer.

Used by many small auth utilities as the common fatal error path.
