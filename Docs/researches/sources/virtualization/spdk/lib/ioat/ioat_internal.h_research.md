# File Research: sources/virtualization/spdk/lib/ioat/ioat_internal.h

`ioat_internal.h` defines private structures and helpers for the I/OAT library.

It includes public IOAT/spec headers, queue macros, and MMIO helpers. `IOAT_DEFAULT_ORDER` sets the default descriptor ring size to `1 << 15` entries. `ioat_descriptor` stores the hardware descriptor physical address plus user callback and callback argument.

`spdk_ioat_chan` is the per-device/channel state: PCI device handle, max transfer size, mapped register pointer, DMA completion-update pointer, ring head/tail, ring size order, last completed descriptor address, software descriptor ring, hardware descriptor ring, DMA capability flags, and global attached-list link.

Inline helpers classify channel status values as active, idle, halted, or suspended based on IOAT status bits.

Research notes: this header’s structures are owned by `ioat.c`; changes affect ring management, hardware programming, and completion polling.
