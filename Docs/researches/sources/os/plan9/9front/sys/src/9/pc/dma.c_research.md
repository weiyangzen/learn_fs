# File Research: sources/os/plan9/9front/sys/src/9/pc/dma.c

## Purpose
PC i8237 DMA controller support with bounce buffers for ISA-style DMA channels that must operate below 16 MiB and cannot cross 64 KiB boundaries.

## Exposed Interface
- `_i8237alloc()`
- `dmainit(int chan, int maxtransfer)`
- `dmabva(int chan)`
- `dmacount(int chan)`
- `dmasetup(int chan, void *va, long len, int flags)`
- `dmadone(int chan)`
- `dmaend(int chan)`

## Implementation Notes
- Defines two DMA controller port maps (`dma[0]`, `dma[1]`) with address/count/page/mode/mask registers and a `shift` for 8-bit vs 16-bit channels.
- `_i8237alloc()` allocates one or two 64 KiB bounce buffers aligned to 64 KiB and below 16 MiB, depending on global `i8237dma`.
- `dmainit()` reserves DMA I/O ports once and assigns a preallocated bounce buffer to a channel.
- `dmasetup()` decides whether a transfer can use the caller buffer directly. It falls back to the channel bounce buffer if:
  - address is not kernel memory,
  - physical range crosses a 64 KiB boundary,
  - physical address is at or above 16 MiB.
- Non-read DMA copies outbound data into the bounce buffer before programming the controller.
- Programming the DMA address, count, page, mode, and mask is done under the controller lock.
- `dmaend()` masks the channel and copies read data from the bounce buffer back to the original destination.

## Filesystem Relevance
Not a filesystem component, but part of the PC kernel device substrate used by legacy storage/network drivers. Important for understanding older block/storage device DMA constraints in Plan 9.

## Risks / Quirks
- Bounce buffers are allocated early and fixed; exhaustion produces `"no i8237 DMA bounce buffer < 16MB"`.
- Maximum transfer is capped at 64 KiB.
- `dmacount()` reads low/high count bytes and adjusts for controller word size.
