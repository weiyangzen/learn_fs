# File Research: sources/os/plan9/plan9/sys/src/9/teg2/mem.h

Shared C/assembly memory-layout and machine-constant header for the Tegra2 port.

Key contents:
- Page, stack, CPU, cache-line, and page-table sizes.
- Register conventions: `R9` as `up`, `R10` as `m`.
- Kernel/user virtual layout: `KZERO`, `L1`, `CONFADDR`, `CACHECONF`, `KTZERO`, `USTKTOP`, `USTKSIZE`.
- Physical MMIO and remapped windows: DRAM, IO, L2 cache controller, EVP, console UART, AHB, NOR.
- PTE flag definitions and reboot trampoline address.

Notes:
- Documents the low-memory layout around Mach, L1/L2 tables, config data, and kernel text.
- `USTKTOP` is kept below 1 GiB to avoid MMIO and high-vector collisions.
