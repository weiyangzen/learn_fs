# File Research: sources/os/plan9/9front/sys/src/9/imx8/mem.h

Role: i.MX8 ARM64 memory layout, page-table geometry, virtual address constants, and PTE attribute definitions.

Key contents:
- Defines KiB/MiB/GiB, 64 KiB pages (`PGSHIFT=16`), effective VA bits (`EVASHIFT=34`), page-table level math, and L1 table sizing.
- Defines CPU/stack constants: `MAXMACH=4`, `MACHSIZE=8 KiB`, `KSTACK=8 KiB`, and `TRAPFRAMESIZE`.
- Defines reserved uncached DRAM at the end of `KZERO` physical space.
- Defines kernel virtual layout: `VDRAM`, `KTZERO`, `VIRTIO`, `KZERO`, `VMAP`, `KMAP`, `KSEG0`, L1/L1BOT/L1TOP, `MACHADDR`, `CONFADDR`, `BOOTARGS`, and `REBOOTADDR`.
- Defines user layout: `UZERO`, `UTZERO`, `USTKTOP`, `USTKSIZE`.
- Defines word/block alignment and map constants.
- Defines shareability, cache memory attributes, MAIR indices, PTE valid/table/page/block bits, AP/SH fields, AF/NG/PXN/UXN bits, and common PTE attribute combinations.
- Defines physical DRAM base and local `MIN`/`MAX`.

Dependencies:
- Used by both C and assembly; changes affect bootstrap, MMU, and trap frame layout.

Notes:
- Comments document physical ranges implied by virtual constants, especially VDRAM and VIRTIO.
