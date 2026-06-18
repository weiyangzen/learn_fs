# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-wrapper.c

## Summary
Wrapper source for building shared SoftFloat code in the SPARC64 architecture directory.

## Key Details
- Contains only `#include <softfloat.c>`.

## Notes
Used when direct use of `softfloat.c` is inconvenient because of `.PATH` interactions.
