# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/buf.c

This file implements simple buffered input for webfs network connections.

Functions:
- `initibuf` initializes fd, `Ioproc`, and buffer read/write pointers.
- `readibuf` first drains buffered bytes, otherwise uses `ioreadn`.
- `unreadline` pushes a line plus newline back in front of unread buffered bytes.
- `readline` reads until newline or EOF, using half the internal buffer at a time, and trims trailing spaces, tabs, carriage returns, and newlines.

Role:
- Used by HTTP response parsing to read status lines and MIME headers while supporting one-line pushback for header continuations.

Notable constraints:
- `unreadline` assumes the internal buffer has enough front space for the pushed line plus unread bytes.
- `readline` truncates lines longer than caller buffer while continuing to consume through newline.
