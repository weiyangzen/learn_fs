# File Research: sources/os/plan9/plan9/sys/src/9/bcm/dma.c

BCM2835 DMA controller support.

Key behavior:
- Uses channels 0-6 only, with channel 4 selected for eMMC by `io.h`.
- Lazily initializes a channel on first `dmastart()`: maps registers, allocates aligned control block, enables channel, resets it, and enables its interrupt.
- Supports device-to-memory, memory-to-device, and memory-to-memory directions.
- Handles cache maintenance before DMA: writeback for sources, writeback+invalidate for destinations.
- Programs DMA control block with bus addresses (`DMAADDR`, `DMAIO`), transfer length, DREQ peripheral mapping, and interrupt enable.
- `dmawait()` sleeps for completion, validates `Cs` status, resets/clears errors on timeout or failure, and acknowledges successful completion.

Primary consumer in this group is `emmc.c`.
