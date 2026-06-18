# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/_rand48.c

Read completely: 59 lines.

Defines the global 48-bit linear congruential generator state: `__rand48_seed[3]`, `__rand48_mult[3]`, and `__rand48_add`. Implements `__dorand48()`, which advances a supplied three-word seed using 16-bit partial products and carry propagation.

All public `rand48` variants in this group depend on this state transition helper.
