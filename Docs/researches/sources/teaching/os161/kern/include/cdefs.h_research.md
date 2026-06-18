# File Research: sources/teaching/os161/kern/include/cdefs.h

Provides common C/compiler support macros.

Key definitions:
- `COMPILE_ASSERT` for compile-time structure/layout checks.
- `ARRAYCOUNT` for static array lengths.
- GCC attributes: `__PF` for printf format checking, `__DEAD` for noreturn, `__UNUSED`.
- `INLINE` abstraction handles C99 and older GCC inline semantics so headers can define inline functions while one source file emits out-of-line copies.

Relevance:
- SFS uses `COMPILE_ASSERT` to validate on-disk structure sizes.
- `array.h`, `semfs.h`, and `membar.h` rely on the inline support pattern.
