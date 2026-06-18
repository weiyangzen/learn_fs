# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/softfloat-for-gcc.h

Read completely: 214 lines.

This header maps SoftFloat internal/public names to GCC soft-float helper symbols. It first moves shared software FP state and comparison primitives into `_softfloat_*` implementation namespace, then defines arithmetic, conversion, comparison, and truncation helpers such as `float32_add -> __addsf3`, `float64_div -> __divdf3`, and `float128_to_int64_round_to_zero -> __fixtfdi`.

It also declares enabled comparison helper name mappings for `floatx80` and contains ARM EABI remaps from GCC helper names to `__aeabi_*` names when `__ARM_EABI__` is defined.

Risk: this is ABI glue. Incorrect macro ordering or missing conditionals can export the wrong symbol name or collide with libgcc-provided helpers.
