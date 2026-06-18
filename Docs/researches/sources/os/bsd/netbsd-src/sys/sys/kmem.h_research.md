# File Research: sources/os/bsd/netbsd-src/sys/sys/kmem.h

Declares NetBSD’s kernel memory allocation API. It provides general and interrupt-context allocation/free routines, zeroing variants, formatted string allocation, string duplication/free helpers, temporary-buffer helpers, and sleep/non-sleep allocation flags.

This is a core allocator interface used throughout kernel code. Risks are matching free sizes with original allocations, choosing `KM_SLEEP` only where sleeping is legal, and using interrupt allocation paths in contexts that cannot block.
