# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/softfloat.h

This header declares the or1k SoftFloat API. Both `FLOATX80` and `FLOAT128` are disabled, while `float32` and `float64` are always defined and mapped to integer storage types.

It declares softfloat rounding, tininess, exception state, integer conversion, float32/float64 arithmetic/comparison/conversion routines, and conditional prototypes for disabled extended/quad blocks. It is mostly identical to other non-extended ports and acts as the compile-time contract between libc softfloat sources and or1k callers.
