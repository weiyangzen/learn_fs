# File Research: sources/os/plan9/plan9/sys/src/9/pc/audio.h

Small PC audio compatibility header.

Key contents:
- Defines buffer size/count, DMA channel, audio IRQ, and byte-swap flag.
- Maps generic audio hooks to PC kernel helpers:
  - `seteisadma(a, b)` to `dmainit(a, Bufsize)`
  - `UNCACHED(type, v)` to a direct cast
  - `setvec(v, f, a)` to `intrenable(..., "audio")`
- Defines `Int0vec` empty.

Role:
- Supplies platform-specific constants/macros expected by shared or legacy audio code.

Notable details:
- `Bufsize` is documented as 5.8 ms and must be a power of two.
- `Nbuf` gives roughly 0.74 seconds total buffering.
