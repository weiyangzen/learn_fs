# File Research: sources/os/bsd/freebsd-src/sys/sys/sbuf.h

Read completely: 123 lines.

## Purpose
Defines the `sbuf` dynamic/fixed string buffer API used for safe formatted string construction and draining.

## Main Elements
- Declares opaque `struct sbuf` and drain callback type.
- Defines `struct sbuf` fields for buffer pointer, drain function/argument, error, size, length, flags, section length, and record offset.
- Defines flags for fixed length, autoextend, include-NUL accounting, drain-to-EOR, nonblocking extend, dynamic buffer/structure, finished state, in-section, and drain-ended-at-EOL.
- Defines hexdump formatting flags if not already present.
- Declares creation, flag access, clear/setpos, binary/string copy/append, printf/vprintf, newline termination, putc, drain setup/drain, trim, error, finish, data/length/done, delete, section start/end, hexdump, drain helpers, and putbuf.
- Kernel side declares uio-backed sbuf creation and copyin helpers plus DDB drain helper.

## Dependencies And Integration
Used by kernel and userland code that builds bounded or dynamically extending strings, sysctl output, diagnostics, hexdumps, and user-copying paths.

## Risk Notes
Consumers must respect `sbuf_finish()` before reading final data and handle sticky error state. Drain callbacks affect buffering semantics and can impose allocation/sleeping constraints.
