# File Research: sources/os/plan9/9front/sys/src/cmd/rc/io.h

Defines the `io` buffer structure and declares all `rc` I/O helpers.

The abstraction is deliberately small: fd, buffer pointers, EOF constant, constructors for fd/string/core input, read/write primitives, flushing, closing, and formatted printing hooks.
