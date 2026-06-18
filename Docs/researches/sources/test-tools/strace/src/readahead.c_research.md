# sources/test-tools/strace/src/readahead.c

Purpose: Decodes the `readahead` syscall.

Important APIs/types/functions: `SYS_FUNC(readahead)`.

Control flow: prints fd, offset, and count in syscall argument order, with fd formatting and numeric offset/count output, then returns decoded.

State and persistence: stateless.

Dependencies/integration: core syscall argument helpers and fd printer.

Risks: offset type width must match kernel argument packing on all personalities.

Test signals: `readahead(fd, offset, count)` golden output with large offsets and invalid fd cases.
