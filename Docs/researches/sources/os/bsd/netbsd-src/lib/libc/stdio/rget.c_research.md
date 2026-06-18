# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/rget.c

Implements `__srget(FILE *)`, the slow path for `getc()` when the current input buffer is empty. It sets byte orientation, calls `__srefill()`, then consumes and returns the first byte from the newly filled buffer.

On refill failure it returns `EOF`.
