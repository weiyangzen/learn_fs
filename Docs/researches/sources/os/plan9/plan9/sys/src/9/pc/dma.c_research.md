# File Research: sources/os/plan9/plan9/sys/src/9/pc/dma.c

Read completely: 264 lines.

This file implements support routines for the i8237 ISA DMA controllers.

Key behavior:
- Defines two DMA controller port maps and per-channel transfer state.
- Allocates low-memory bounce buffers below 16 MB for ISA DMA.
- `dmainit()` reserves DMA controller I/O ports and assigns a bounce buffer to a channel.
- `dmasetup()` programs DMA controller address, page, count, and mode registers.
- Uses bounce buffers when memory is user-space, crosses a 64 KB boundary, or is above 16 MB.
- `dmadone()` checks terminal count status.
- `dmaend()` disables the channel and copies read data out of the bounce buffer when needed.

Important interfaces:
- Public functions: `_i8237alloc`, `dmainit`, `dmasetup`, `dmadone`, `dmaend`.
- Uses `xspanalloc()`, `PADDR()`, `ioalloc()`, `outb/inb`, and interrupt locks.

Research notes:
- Maximum transfer is clamped to 64 KB.
- 16-bit DMA channels use `shift = 1`, affecting address/count programming.
- The commented `dmacount()` helper is present but disabled.
