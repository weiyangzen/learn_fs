# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/net/Makefile.inc

AArch64 libc net build fragment.

Key behavior:
- Contains only a comment noting that `hton*` and `nto*` functions are provided by `../gen/byte_swap_*.S`.

Dependencies:
- Generic architecture byte-swap assembly sources.
