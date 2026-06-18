# File Research: sources/os/plan9/9front/sys/src/cmd/aux/zerotrunc.c

Copies stdin to stdout until the first zero byte.

Key responsibilities:
- Reads input in 4096-byte chunks.
- Searches each chunk for `'\0'`.
- Writes only bytes before the first zero byte.
- Stops after encountering a zero byte or EOF.

Important interfaces:
- Standalone Plan 9 libc command.

Notes:
- Intended for truncating null-terminated data streams without including the terminator.
