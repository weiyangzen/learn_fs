# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.cc

## Purpose
Provides Mark Adler's CRC32C implementation adapted for XRootD C++ builds, with x86_64 SSE4.2 hardware acceleration and portable software fallback.

## Important APIs and control flow
On x86_64, helper functions build GF(2) zero-shift operators and lookup tables so the hardware path can process three independent streams over large `LONG` and `SHORT` blocks, combine them, and then finish aligned eight-byte and trailing byte segments using inline `crc32` assembly. `crc32c()` checks SSE4.2 via `cpuid` on each call and chooses hardware or software. On non-x86_64, it always calls `crc32c_sw()`.

The software path lazily initializes little-endian or big-endian slicing-by-8 tables with `pthread_once`. `crc32c_sw_little()` and `crc32c_sw_big()` pre/post invert CRC state, align to eight bytes, process table-driven words, and finish trailing bytes. The `TEST` block can compile a standalone stdin benchmark/checksum tool.

## State, dependencies, and integration
State consists of static lookup tables and `pthread_once_t` guards. The public functions are declared in `XrdOucCRC32C.hh` and wrapped by `XrdOucCRC`. Dependencies include pthreads, inline assembly, and endian byte swapping.

## Risks and test signals
The x86 `SSE42` macro uses inline asm clobbering `%ebx`, which can be sensitive under PIC/toolchain differences. CPU feature detection occurs every call rather than cached. Tests should compare hardware and software CRCs for known vectors and random buffers, run under non-SSE emulation if possible, and cover unaligned pointers and big-endian builds.
