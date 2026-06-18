# File Research: sources/os/plan9/9front/sys/src/9/omap/dma.c

OMAP system DMA support.

Key behavior:
- Defines SDMA controller and channel register layouts.
- `dmainit` resets the DMA controller, clears interrupts, disables channels, and installs interrupt handlers.
- `dmastart` allocates a DMA channel/IRQ slot, configures source/destination addressing modes, rounded transfer length, block-complete interrupt, and starts the channel.
- `dmaintr` acknowledges DMA completion, marks the caller’s `done` flag, wakes the caller rendezvous, and disables the channel/IRQ.
- `isdmadone` reports completion state for a DMA IRQ slot.
- `dmatest` allocates scratch memory and runs a simple fill/copy validation using DMA.

Research notes:
- The implementation maps DMA channels one-to-one with IRQ slots and panics if all slots are in use.
- Cache coherency is caller-sensitive; the test path explicitly invalidates cache after DMA.
