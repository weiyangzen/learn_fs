# File Research: sources/os/plan9/9front/sys/src/9/arm64/mem.c

Initial ARM64 kernel memory map creation and RAM discovery.

Key behavior:
- Builds a temporary TTBR0 identity map for DRAM below `-KZERO`.
- Builds the initial shared TTBR1 kernel page table for early DRAM and VIRTIO I/O.
- Handles misaligned VIRTIO mappings by falling back to page mappings.
- Seeds higher-level kernel table pointers when more page-table levels are required.
- `meminit` derives memory limit from `*maxmem` or a default, maps RAM into the kernel map, and populates `conf.mem[0]`.

Dependencies:
- Uses page table constants from `mem.h`, `kmapram`, and boot config.

Research notes:
- Early page tables cover just enough for kernel startup and device I/O; `meminit` fills RAM mappings later.
