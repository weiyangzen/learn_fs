# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/glue.h

Defines `struct glue`, the linked-list node used to manage dynamically allocated arrays of `FILE` objects after the statically allocated initial streams. Each node records the next node, number of `FILE` objects, and pointer to the object array.

It declares the global `__sglue`, making this header part of stdio stream-allocation internals.
