# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negdf2.c

Read completely: 24 lines.

Defines `__negdf2` for double-precision negation. It flips the sign bit with XOR using `FLOAT64_MANGLE(0x8000000000000000ULL)`.

Risk: bit-level sign toggle preserves NaN payloads and zeros; correctness depends on the `FLOAT64_MANGLE` ABI representation hook.
