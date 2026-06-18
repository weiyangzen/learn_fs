# File Research: sources/os/plan9/9front/sys/src/9/lx2k/mem.h

LX2K ARM64 memory and MMU constants. It defines 4 KiB pages, effective 34-bit virtual addressing, multi-level page-table index macros, kernel/user virtual layout, TTBR0/TTBR1 page-table placement, Mach placement, boot args, reboot address, memory attributes, ARM64 PTE bits, and physical I/O/DRAM bases.

The layout maps DRAM through high virtual aliases (`VDRAM`, `KZERO`, `KSEG0`, `KMAP`, `VMAP`) and maps MMIO through `VIRTIO`. It defines ARM64 memory attribute indexes for write-back/write-through/uncached/device memory and access/shareability/execute-never flags.

Notable risks: `MAXMACH` is one despite MP scaffolding elsewhere; page-table macros are nontrivial and shared with assembly.
