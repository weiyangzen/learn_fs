# File Research: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/sparc_v8.S

SPARC v8 assembly implementations of GCC helper arithmetic entry points.

Key behavior:
- Exports `.umul`, `.mul`, `.udiv`, `.div`, `.urem`, and `.rem`.
- `.umul`/`.mul` return low 32 bits in `%o0` and high 32 bits from `%y` in `%o1`.
- `.udiv`/`.div` seed `%y`, include delay nops, and return quotient in `%o0`.
- `.urem`/`.rem` compute quotient, multiply quotient by divisor, and subtract to return remainder.

Dependencies:
- SPARC v8 multiply/divide instructions and `%y` register semantics.

Notes:
- This is compiler support code placed in a separate v8 library for systems where libc versions are not appropriate.
