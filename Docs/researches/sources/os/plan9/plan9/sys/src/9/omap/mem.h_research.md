# File Research: sources/os/plan9/plan9/sys/src/9/omap/mem.h

OMAP memory layout and machine constant header shared by C and assembly.

Key contents:
- Defines binary size units, bit-field helpers, page/stack/cache sizes, and max CPU count.
- Defines kernel/user virtual address layout:
  - `KZERO`/`KSEG0` at `0xC0000000`.
  - `L1` page table at `KZERO+16KiB`.
  - `CONFADDR` at `KZERO+0x300000`.
  - `KTZERO` at `KZERO+0x310000`.
  - user top at `0x20000000`.
- Defines reboot trampoline address `REBOOTADDR`.
- Defines Plan 9 PTE flags: valid, write, uncached, kernel.
- Enumerates OMAP35 physical peripheral addresses: system control, DSS/DISPC, DMA, USB, UARTs, MMC, INTC, PRM, watchdogs, timers, GPIO, L3/L4, GPMC, and DRAM.
- Defines `VIRTIO` as the same address as `PHYSIO`, relying on direct MMIO mapping.

Role:
- Provides the hardware contract for startup assembly, MMU setup, traps, screen, UART, USB, and other device drivers.
- Documents the low-memory boot layout used by `l.s`, `mmu.c`, `main.c`, and `rebootcode.s`.

Notable constraints:
- `MAXMACH` is 1.
- `KSEGM` mask assumes 512 MiB DRAM.
- Comments warn `KTZERO` must match the kernel mkfile load address.
