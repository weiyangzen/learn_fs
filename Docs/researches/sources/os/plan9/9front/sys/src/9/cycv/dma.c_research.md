# File Research: sources/os/plan9/9front/sys/src/9/cycv/dma.c

Cyclone V DMA controller microprogramming support.

Key responsibilities:
- Maps DMA controller registers.
- Defines DMA channel/status/control and instruction encodings.
- Builds compact DMA instruction streams for memory copies.
- Supports burst/beat sizing and source/destination increment attributes.
- Waits for transfer completion through interrupt wakeups.
- Provides DMA abort interrupt handling.
- Registers DMA interrupt handlers in `dmalink()`.

Important behavior:
- `compactify()` removes no-op spacing from generated instruction streams.
- `dmacopy()` uses controller microcode rather than CPU copy loops.
- DMA completion waits on controller state and interrupt paths.

Dependencies:
- Cyclone V DMA registers, interrupt controller, cache/coherence helpers, and `SRC_INC`/`DST_INC` attributes from `dat.h`.
