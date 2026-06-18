# File Research: sources/os/plan9/9front/sys/src/9/bcm64/mem.c

ARM64 BCM initial mapping and physical memory discovery.

Key responsibilities:
- Creates identity mappings for TTBR0 during early boot in `mmuidmap()`.
- Creates shared kernel mappings for KZERO, VIRTIO, and ARMLOCAL in `mmu0init()`.
- Handles mixed block/page mappings when I/O ranges are not block-aligned.
- Discovers RAM from mailbox or `*maxmem` overrides.
- Trims memory to SoC DRAM size and virtual KMAP limits.
- Removes oversized early mappings and remaps actual RAM through `kmapram()`.
- Counts pages per configured memory bank.

Important behavior:
- `INITMAP` ensures the kernel image plus one page is mapped during transition.
- Memory above actual RAM is explicitly unmapped after discovery.

Dependencies:
- ARM64 PTE macros, SoC physical I/O layout, mailbox RAM query, `conf.mem`, TLB flush, and kernel end symbol.
