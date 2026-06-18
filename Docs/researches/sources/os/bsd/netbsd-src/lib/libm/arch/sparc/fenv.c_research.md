# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/sparc/fenv.c

SPARC fenv implementation using `%fsr` load/store inline assembly. It maps exception flags, rounding bits, trap-enable masks, and current accrued exceptions through SPARC FSR fields.

Implements full fenv operations plus exception enable/disable extensions. `feraiseexcept()` uses volatile floating-point operations to trigger requested exceptions.
