# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/block.c

Implements the PPP `Block` buffer allocator and block-chain manipulation routines.

Key behavior:
- `allocb` allocates blocks with front padding and reuses free-list buckets.
- `freeb` returns a chain to bucketed free lists and poisons pointers to catch use-after-free.
- `concat`, `blen`, `pullup`, `padb`, `btrim`, `copyb`, and `pullb` manipulate chained packet buffers.
- Optional allocation tracing records caller PCs under `ADEBUG`.

Integration points:
- Used throughout PPP framing, compression, checksum, and IP data paths.
- Shared `Block` structure is declared in `ppp.h`.

Risks and notes:
- Free-list bucket selection is approximate: `(bsz >> 10) & 31`.
- `pullup` can allocate a new leading block if the first block lacks room, then pulls data from following blocks.
