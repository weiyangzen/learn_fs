# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printbuf.c

Printable/escaped buffer printer.

Key behavior:
- Emits printable bytes directly.
- Emits non-printable bytes as octal escapes.
- Stops at NUL when `zend` is nonzero.

Research notes:
- Uses current locale’s `isprint()` behavior.
