# File Research: sources/local-fs/xfsdump/include/swab.h

`swab.h` provides byte-swapping primitives for 16-, 32-, and 64-bit XFS integer types.

Key content:
- Defines expression-style swap macros `___swab16`, `___swab32`, and `___swab64`.
- Defines constant-form macros `___constant_swab16`, `___constant_swab32`, and `___constant_swab64`.
- Provides fallback architecture hooks `__arch__swab16/32/64`, pointer forms, and in-place forms when no arch-specific versions are defined.
- Defines public `__swab16`, `__swab32`, and `__swab64` using `__builtin_constant_p` for compile-time folding.
- Provides inline functions `__fswab16`, `__swab16p`, `__swab16s`, and equivalents for 32/64-bit values.
- Supports `__SWAB_64_THRU_32__` to implement 64-bit swapping using two 32-bit swaps.

Dependency:
- Assumes XFS/Linux-style integer typedefs such as `__u16`, `__u32`, and `__u64` are already available.

Portability note:
- Uses GNU C statement expressions and `__builtin_constant_p`, so it is compiler-extension-dependent.
