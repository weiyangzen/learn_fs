# File Research: sources/os/plan9/9front/sys/src/9/bcm64/mem.h

ARM64 BCM memory layout, virtual address scheme, page-table constants, and PTE attributes.

Key contents:
- Defines 4 KiB pages, VA width, page-table levels, index macros, and block/page sizes.
- Defines `MAXMACH`, stack sizes, trap-frame size, and per-CPU `Mach` address layout.
- Defines high-half kernel ranges for KMAP, VMAP, VIRTIO2/VIRTIO1/VIRTIO, ARMLOCAL, VGPIO, VDRAM, KZERO, KTZERO, and user space.
- Defines memory attribute encodings, shareability, PTE validity/type/access/cache/execute bits.
- Defines segment-map sizing and Plan 9 PTE abstraction flags.

Role:
- Core ABI shared by ARM64 BCM assembly, MMU, drivers, and port code.

Notable constraints:
- User top is derived from the effective VA mask.
- Kernel layout leaves fixed low offsets for spin table, config, reboot code, and mailbox buffer.
