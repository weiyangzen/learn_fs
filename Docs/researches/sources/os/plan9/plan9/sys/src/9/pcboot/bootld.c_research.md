# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/bootld.c

## Purpose
Streaming kernel loader for the PC bootstrap environment. It recognizes Plan 9 exec images, ELF32, ELF64, and gzip-wrapped Plan 9 kernels, loads segments into target memory, and jumps to the kernel.

## Main Interfaces
- Exports `bootpass(Boot *b, void *vbuf, int nbuf)`.
- Exports `impulse()`, `warp9(ulong entry)`, and `prstackuse(int)`.
- Uses external assembly helpers `pagingoff` and `warp64`.

## Implementation Notes
- Maintains a state machine in `Boot.state` with states defined in `dat.h`.
- Provides endian-swapping helpers for ELF headers and program headers.
- ELF32/ELF64 paths read the ELF header, program headers, skip padding without rewind, stream `LOAD` segments to physical addresses, zero BSS tails, and record entry.
- Plan 9 exec path handles `I_MAGIC` and `S_MAGIC`, loads text and data, zeroes BSS, and then boots.
- Gzip path buffers compressed input up to `Kernelmax`, probes the uncompressed exec header with `gunzip`, decompresses full text+data, page-aligns data, and boots.
- `impulse` drains UART output, raises SPL, disables buffered serial output, shuts down devices, and turns interrupts off before transfer.
- Boot transfer uses Multiboot register conventions for ELF/Plan 9 handoff.

## Dependencies And Risks
- Streaming ELF loader cannot rewind, so `LOAD` segments whose file offsets precede `curoff` fail.
- Kernel size and entry are checked against low-memory and `Kernelmax` constraints.
- Gzip decompression uses a fixed allocation and assumes the uncompressed payload is a Plan 9 boot image.
