# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits64/softfloat.c

Read completely: 5647 lines.

This is the 64-bit-integer implementation of John Hauser's SoftFloat Release 2a as adapted for NetBSD libc and GCC soft-float helper generation. It implements IEC/IEEE floating-point conversions, arithmetic, rounding, exception flagging, NaN handling hooks, and comparisons for `float32`, `float64`, optional `floatx80`, and optional `float128`.

Key elements: global software FP state defaults to round-to-nearest-even and zero exception flags unless architecture hooks override setters; `softfloat-macros` supplies multiword integer arithmetic; `softfloat-specialize` supplies target NaN, tininess, and exception policy. The core is organized by format: extraction/packing, subnormal normalization, round-and-pack helpers, integer conversions, inter-format conversions, round-to-integer, add/subtract/multiply/divide/remainder/sqrt, and ordered/quiet/signaling comparisons.

NetBSD/GCC interactions: `SOFTFLOAT_FOR_GCC` includes `softfloat-for-gcc.h` to rename SoftFloat APIs to compiler helper symbols such as `__adddf3` and to omit routines provided elsewhere by libgcc. `FLOAT64_DEMANGLE`/`FLOAT64_MANGLE`, `X80SHIFT`, `X80M68K`, and unsigned-fix conversion conditionals support architecture ABI quirks.

Behavior/risks: this is foundational arithmetic code; correctness depends on exact bit-level rounding, sticky-bit jamming, NaN propagation, and exception-flag behavior. State is stored in global variables unless platform-specific hooks provide a different backing, so callers expecting thread-local FP state must rely on the surrounding libc/architecture integration.
