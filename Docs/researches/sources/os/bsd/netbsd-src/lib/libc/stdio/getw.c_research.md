# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getw.c

Implements historical `getw(FILE *)`. It reads one raw `int` object with `fread()` and returns it on success, otherwise returns `EOF`.

The function is binary-format and host-endian dependent; it provides compatibility rather than portable serialization.
