# File Research: sources/os/plan9/9front/sys/src/9/mtx/mem.h

This header defines MTX PowerPC memory, page, cache, SPR, exception, MMU, and platform address constants.

It sets 4K pages, 16-byte cache lines, 4K kernel stacks, PowerPC SPR numbers, BAT register numbers, 604e-specific SPRs, MSR bit encodings, exception vector codes, magic registers (`MACH` and `USER`), hashed page-table constants, PTE encodings, user/kernel virtual layout, PCI memory windows, I/O memory window, Raven/Falcon/flash addresses, and page-color macros.

Filesystem relevance is foundational: page size, user stack/text addresses, PTE permissions/cache bits, and PCI/I/O address ranges drive memory-mapped file handling, page faults, DMA buffers, and device access.

Notable risks: `isphys` uses `KZERO` direct-map convention; PCI/I/O window constants must match `raven.c`; cache coloring is disabled via `getpgcolor(a) 0`.
