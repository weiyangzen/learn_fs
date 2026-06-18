# File Research: sources/os/bsd/dragonflybsd/sys/sys/in_cksum.h

`in_cksum.h` defines Internet checksum helpers. It includes `sys/types.h` and `machine/stdint.h`.

Kernel-only declarations include `in_cksum_range()` for mbuf ranges and `asm_ones32()` for 32-bit-word summing, plus inline wrappers `in_cksum()`, `in_cksum_skip()`, and `in_cksum_hdr()` for IPv4 headers.

The header also provides inline assembly helpers `in_addword()` and `in_pseudo()` for one's-complement addition and pseudo-header checksum folding. The inline assembly makes this architecture-specific despite being under `sys`.
