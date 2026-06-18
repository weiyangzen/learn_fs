# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/unthwack.c

THWACK decompressor implementation.

Key behavior:
- `unthwackinit()` clears decoder state and points block data fields at fixed storage.
- `unthwackstate()` returns the newest sequence and bitmask of nearby available history blocks for compressor acknowledgments.
- `unthwackinsert()` inserts decoded blocks into sequence-ordered history, rotating the decode window.
- `unthwackadd()` stores an uncompressed block in decoder history.
- `unthwack()`:
  - Validates compressed block size.
  - Reconstructs history block set from sequence delta and mask.
  - Decodes adaptive literals, variable-length match lengths, and match offsets.
  - Copies reconstructed output to caller buffer and inserts it into history.
  - Writes human-readable decode errors into `ut->err`.

Integration:
- Called by `thw.c` decompression path.
- Wire-format counterpart to `thwack.c`.

Risks and notes:
- Detects common corruption modes: missing history, output overflow, offset/length invalidity, compressed overrun.
- Uses static maximum block sizes and fixed per-window buffers.
