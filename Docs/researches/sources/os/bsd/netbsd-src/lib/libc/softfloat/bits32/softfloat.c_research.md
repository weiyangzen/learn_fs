# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits32/softfloat.c

This file is NetBSD’s bits32 variant of John Hauser’s SoftFloat Release 2a, adapted for GCC `-msoft-float`. It implements software IEEE-style single-precision and double-precision operations using 32-bit word arithmetic. This variant notes that `float64` is represented as a 64-bit integer rather than the original two-word structure, with `FLOAT64_MANGLE`/`FLOAT64_DEMANGLE` hooks for platform representation.

Global softfloat state is provided when not supplied externally: `float_rounding_mode` defaults to nearest-even, and `float_exception_flags` records raised exceptions. Target-specific behavior is pulled from `softfloat-specialize`, while primitive multiword arithmetic and estimates come from `softfloat-macros`.

The file defines low-level helpers for extracting, normalizing, packing, rounding, and overflow/underflow handling:
- single helpers extract sign/exponent/fraction, normalize subnormals, pack fields, and `roundAndPackFloat32`;
- double helpers extract high/low fraction words from the 64-bit value, normalize subnormals, pack fields through `FLOAT64_MANGLE`, and `roundAndPackFloat64`;
- normalization wrappers handle unnormalized significands before final rounding.

Always-built conversion and operation exports include integer-to-float conversions, float-to-int round-to-zero conversions, float32/float64 widening/narrowing, add/subtract/multiply/divide for float32 and float64, and ordered comparisons `eq`, `le`, and `lt`. These implement IEEE special cases: NaN propagation, infinity handling, signed zeros, divide-by-zero, invalid operations such as infinity minus infinity or zero times infinity, and inexact/underflow/overflow flagging.

Additional functions are compiled only when `SOFTFLOAT_FOR_GCC` is not defined. These include current-rounding-mode integer conversions, round-to-integer, remainder, square root, signaling comparisons, and quiet comparison variants for both float32 and float64.

The arithmetic structure is classic SoftFloat:
- addition/subtraction split into same-sign significand addition and opposite-sign subtraction helpers;
- multiplication uses 32x32 or 64x64-to-128 intermediate products;
- division uses quotient estimates with correction loops;
- square root uses estimate functions plus remainder correction;
- comparisons explicitly handle NaNs and signed-zero equality.

Research notes and risks:
- This file’s normal libc build path defines `SOFTFLOAT_FOR_GCC` via the makefiles, excluding many non-GCC helper functions.
- Several non-`SOFTFLOAT_FOR_GCC` double routines still use `.high` and `.low` member syntax even though the file header says `float64` is a 64-bit integer in this NetBSD variant. That is likely harmless for the default GCC-support build but is a compatibility risk if building the full non-GCC bits32 file as-is.
- Correctness relies heavily on `softfloat-macros` and `softfloat-specialize`, especially NaN classification/propagation, tininess policy, exception raising, and multiword arithmetic.
- This code is central ABI support for soft-float targets; regressions would affect compiler-emitted floating-point helper calls and libc floating-environment behavior.
