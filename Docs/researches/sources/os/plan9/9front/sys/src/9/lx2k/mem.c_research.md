# File Research: sources/os/plan9/9front/sys/src/9/lx2k/mem.c

LX2K early memory and initial page-table setup. `mmuidmap` creates a temporary TTBR0 identity map for virtual DRAM during early boot. `mmu0init` creates the shared kernel TTBR1 mappings for initial DRAM and `VIRTIO`, including page-level mappings for unaligned MMIO tails and higher-level table links when needed.

`meminit` records available DRAM from the end of the kernel up to 4 GiB, maps it with `kmapram`, and optionally adds a second high-memory region using the `*maxmem` configuration variable.

Notable risks: memory layout is hard-coded for GPP DRAM region 1 and optional region 2; comments note the initial shared table is later completed by `meminit`.
