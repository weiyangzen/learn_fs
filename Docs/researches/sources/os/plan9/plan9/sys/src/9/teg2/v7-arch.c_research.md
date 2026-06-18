# File Research: sources/os/plan9/plan9/sys/src/9/teg2/v7-arch.c

Small ARMv7 helper routines outside cache-specific assembly.

Key behavior:
- `ispow2(uvlong)`: returns whether a 64-bit value is a power of two.
- `log2(ulong)`: returns the exponent of the smallest power of two greater than or equal to `n`, using `clz`.

Notes:
- Filename avoids `arch*.c` because Plan 9 mk scripts treat that pattern specially.
- Comments expect these helpers to be cheap and replaceable once `5c` improves `vlong` codegen.
