# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitops.h

Defines internal macros for portable chunk-based bitmap bit operations.

Key definitions:
- Establishes that bitmap bits and bytes are processed in big-endian order for source data used by `copy_mono`.
- Defines chunk size, byte count, bit count, log2 size, masks, alignment, and all-bits/high-bits macros.
- Includes compiler-workaround definitions for full-width masks and high-bit masks.
- Provides `inc_ptr` for byte-wise pointer arithmetic.
- Defines mono-bit left/right/thin masks differently for big-endian and little-endian architectures.
- Externally declares mask tables used by little-endian mono copy/fill paths.

Dependencies:
- Includes `gsbitops.h` for lower-level bit operation definitions and `mono_fill_chunk_bytes` context.

Research notes:
- The macros are intentionally conservative around old compiler bugs and architectures that cannot shift a full-width long.
