# File Research: sources/os/plan9/9front/sys/src/9/teg2/v7-arch.c

Small ARMv7 utility routines.

Purpose:
- Provides cheap integer helpers outside cache assembly.

Key behavior:
- `ispow2` tests whether a `uvlong` is a power of two.
- `log2` returns the exponent of the smallest power of two greater than or equal to an input `ulong`, using `clz`.

Integration:
- Depends on ARM `clz` from `l.s`.
- Used by architecture/cache sizing code.

Risks/notes:
- `log2(0)` returns one greater than the computed CLZ-derived base, as intended by its “ceil log2” contract but worth preserving if reused.
