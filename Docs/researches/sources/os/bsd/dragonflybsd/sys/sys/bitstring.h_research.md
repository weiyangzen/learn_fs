# File Research: sources/os/bsd/dragonflybsd/sys/sys/bitstring.h

Read completely: 195 lines.

This header implements a byte-array bitstring macro library.

Key contents:
- `bitstr_t` as unsigned char.
- Helpers for byte index and bit mask.
- Macros for sizing, heap allocation, stack declaration, testing, setting, clearing, range clear/set, first clear bit, first set bit, last set bit, and clear-range search.

Security/reliability notes:
- Macro arguments may be evaluated multiple times in some simple helpers; callers should avoid side effects.
- No bounds checking is performed beyond some final comparisons in search macros.
- `bit_alloc()` depends on `calloc()` being visible to the including translation unit.
