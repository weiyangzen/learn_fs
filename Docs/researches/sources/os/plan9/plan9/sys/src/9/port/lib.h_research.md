# File Research: sources/os/plan9/plan9/sys/src/9/port/lib.h

Purpose: Kernel-side declarations and constants for libc-like routines and user-visible Plan 9 ABI structures.

Contents:
- Defines utility macros `nelem`, `offsetof`, and `assert`.
- Declares memory, string, UTF/rune, formatting, conversion, tokenization, base64 decode, qsort, and miscellaneous libc-derived routines.
- Defines UTF constants, mount flags, open flags, note actions, `ERRMAX`, `KNAMELEN`, qid type bits, dir mode bits.
- Defines `Qid`, `Dir`, old wait message, and wait message structures.
- Provides vararg-check pragmas for kernel formatting.

Dependencies and integration:
- Included throughout port and architecture kernel code.
- Bridges kernel code to libc-style helper implementations linked into the kernel.

Risks and notes:
- `assert(x)` stringifies as literal `"x"` in this header’s macro.
- This file carries ABI-shaped definitions used by filesystem/device code.
