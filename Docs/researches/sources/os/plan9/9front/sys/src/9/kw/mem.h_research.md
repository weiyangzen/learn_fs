# File Research: sources/os/plan9/9front/sys/src/9/kw/mem.h

Kirkwood memory-layout and page-table constants shared by C and assembly. It defines page size, stack sizes, kernel/user address ranges, boot-args location, page-table/Mach placement, reboot-code address, clock constants, cache line size, software PTE flags, and physical SoC regions.

The layout maps physical DRAM at `KZERO` (`0x60000000`), starts kernel text at `KZERO+0x800000`, stores early config at `KZERO+4 KiB`, reserves page tables/Mach near `KZERO+64 KiB`, and uses `VIRTIO == PHYSIO` for MMIO.

It also defines physical addresses for DRAM, internal registers, UART, NAND variants, boot ROM, and CESA SRAM.

Notable risks: comments document fragile early memory placement around U-Boot, vectors, Mach, and L1/L2 PTE storage.
