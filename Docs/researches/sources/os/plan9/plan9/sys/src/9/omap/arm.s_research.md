# File Research: sources/os/plan9/plan9/sys/src/9/omap/arm.s

Provides shared OMAP ARM assembly macros for address translation, barriers, cache/TLB maintenance, UART debug output, and PTE filling.

Key points:
- Defines `KADDR()`/`PADDR()` assembly forms based on `KZERO`, `PHYSDRAM`, and `KSEGM`.
- Defines `L1X()` for L1 translation-table index calculation.
- Defines `MACHADDR`, section PTE attribute constants for DRAM and I/O, and low-DRAM double-map size.
- Provides `DELAY` busy-loop and `PUTC` macro for direct console register output.
- Defines ARMv7 instruction encodings unavailable as assembler mnemonics: `SMC`, `WFI`, `DMB`, `DSB`, `ISB`, `NOOP`, `CLZ`, `CPSIE`, `CPSID`, `VMRS`, and `VMSR`.
- Provides branch-target cache flush macros (`FLBTC`, `FLBTSE`) using CP15.
- Defines `BARRIERS` as branch-target-cache flush plus DSB/ISB.
- Provides `FILLPTE()` and `ZEROPTE()` macros for boot-time page table population.

Dependencies and interactions:
- Shared by low-level OMAP assembly such as `l.s` and reboot code.
- Uses constants from `mem.h` and `arm.h`.
- Supports early boot before full C runtime and MMU setup are stable.

Research relevance:
- Assembly utility layer for OMAP boot/MMU/cache setup.
