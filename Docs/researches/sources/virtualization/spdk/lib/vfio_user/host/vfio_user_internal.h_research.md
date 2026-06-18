# File Research: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_internal.h

This private header defines shared vfio-user host structures and internal function declarations.

It sets vfio-user protocol version constants to major 0, minor 1. It defines maximum memory regions as 16 and maximum sparse mmap regions per BAR as 8.

`struct vfio_memory_region` tracks IOVA, size, virtual address, mmap offset, fd, and list linkage for DMA mappings. `struct vfio_sparse_mmaps` records one mapped sparse BAR range. `struct vfio_pci_region` stores BAR offset, size, flags, sparse mmap count, and sparse mmap entries. `struct vfio_device` stores socket fd, generated name, socket path, PCI region array, flags, SPDK memory map, and the DMA memory-region list.

The declarations connect `vfio_user.c` protocol helpers with `vfio_user_pci.c` PCI setup: device setup, device/region info queries, DMA map/unmap, MMIO access, and a fuzzing-only raw request sender.

The header is Linux-specific through `<linux/vfio.h>` and vfio-user protocol structures.
