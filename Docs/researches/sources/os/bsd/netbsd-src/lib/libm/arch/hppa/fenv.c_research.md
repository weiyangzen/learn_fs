# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/hppa/fenv.c

HPPA fenv implementation using inline assembly to read/write the floating-point state register through `%fr0`. It shifts exception flags between status and enable-bit layouts, handles rounding modes, and implements environment save/restore.

`feraiseexcept()` triggers exceptions through volatile floating-point operations rather than only setting flags.
