# File Research: sources/os/plan9/9front/sys/src/9/bcm/dma.c

BCM2835 DMA controller support for channels 0-6.

Key behavior:
- Defines DMA register and control block formats.
- Converts CPU virtual addresses to peripheral bus addresses with `soc.busdram`.
- Converts VIRTIO device addresses to bus I/O addresses with `soc.busio`.
- Lazily initializes DMA channels, allocates aligned control blocks, enables channel registers, and registers interrupts.
- Starts device-to-memory, memory-to-device, and memory-to-memory transfers.
- Uses cache clean/invalidate around source, destination, and control blocks.
- Waits for interrupt completion with timeout, reports errors, and resets failed channels.

Dependencies:
- Uses interrupt registration, cache maintenance, SoC address mapping, and Plan 9 sleep/rendezvous.

Research notes:
- Comments note only a subset of channels work reliably for MMC.
