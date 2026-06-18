# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/chat.c

Provides logging and panic helpers for `ext2srv`.

Key behavior:
- `chat()` writes formatted diagnostic output only when global `chatty` is non-zero.
- `mchat()` always writes formatted output to stderr.
- `panic()` prefixes messages with `argv0` and process id, includes `%r`, then exits with status `panic`.

Dependencies:
- Used by the ext2 server request handlers, filesystem implementation, and buffer cache for diagnostics.
- Relies on Plan 9 varargs formatting and `write(2, ...)`.

Risks and invariants:
- Fixed 1024-byte buffers truncate long formatted messages through `vseprint()`.
- `panic()` terminates the process and is used for invariant violations such as exhausted buffers.
