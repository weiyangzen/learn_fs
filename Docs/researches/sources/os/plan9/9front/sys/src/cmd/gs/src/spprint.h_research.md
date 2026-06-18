# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spprint.h

Declares stream output and fixed-arity printing helpers.

Key points:
- Provides an opaque `stream` declaration.
- Defines `stream_putc`, `stream_write`, and `stream_puts`.
- Declares float, int, long, and string printing helpers.
- Comments explain the PDF-specific no-exponential float requirement and the portability reason for avoiding varargs.

Research relevance:
- Header contract for portable stream formatting utilities.
