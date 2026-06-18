# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fesetexceptflag.c

Implements `fesetexceptflag`.

Key behavior:
- Converts requested exception set to softfloat mask bits.
- Replaces only those sticky bits with the translated contents of `*flagp`.
- Preserves unrelated sticky flags.
- Always returns 0.
