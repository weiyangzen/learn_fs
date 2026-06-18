# File Research: sources/os/bsd/dragonflybsd/sys/sys/hash.h

`hash.h` provides simple 32-bit non-cryptographic hash helpers using the classic `hash * 33 + c` step. It defines `HASHINIT` as 5381 and `HASHSTEP()` if not already defined.

Inline helpers hash arbitrary buffers, null-terminated strings, bounded strings, strings terminated by a specific character, and bounded strings terminated by a specific character. The terminating variants optionally return the end pointer.

The comments note pathname component hashing as a main use case.
