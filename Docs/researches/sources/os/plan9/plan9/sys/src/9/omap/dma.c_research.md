# File Research: sources/os/plan9/plan9/sys/src/9/omap/dma.c

Implements basic OMAP3530 system DMA controller initialization, interrupt handling, and memory copy start support.

Key points:
- Defines register layout for the system DMA controller, including IRQ status/enable, reset/status/config, capabilities, global control, and 32 channel register blocks.
- Uses 4 DMA IRQ/channel slots (`Nirq=4`) starting at IRQ 12.
- `isdmadone()` checks a channel’s block-complete bit.
- `dmaintr()` marks the associated transfer done, wakes its rendezvous, verifies/clears block interrupt status, disables its IRQ bit, and releases transfer state.
- `dmainit()` verifies the controller, soft-resets it, clears all channels and interrupt registers, sets global burst size, and installs IRQ handlers for DMA0-DMA3.
- `dmatest()` runs a test DMA copy to scratch DRAM, waits for completion, invalidates cache, and verifies data and overrun behavior.
- `dmastart()` allocates a free DMA IRQ/channel, records completion rendezvous and flag, programs source/destination physical addresses, address modes, element/frame counts, block interrupt, enables the IRQ, and starts the channel.
- Transfers are rounded up to word size and use word-sized elements.

Dependencies and interactions:
- Used by hardware drivers needing DMA, though `ether9221.c` currently avoids DMA.
- Requires cache maintenance on callers for coherent memory.
- Uses `intrenable()` and OMAP physical DMA address constants.

Research relevance:
- Small but important DMA substrate for OMAP peripherals and future block/data movement paths.
