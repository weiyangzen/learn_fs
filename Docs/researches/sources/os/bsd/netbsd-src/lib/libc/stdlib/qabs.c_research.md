# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/qabs.c

Implements `qabs(quad_t)` as the quad-width absolute value helper. It returns `-j` for negative input and `j` otherwise.

Like traditional `abs`-family functions, the most-negative representable value is subject to signed overflow semantics.
