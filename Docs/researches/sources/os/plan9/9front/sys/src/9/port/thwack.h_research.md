# File Research: sources/os/plan9/9front/sys/src/9/port/thwack.h

Shared interface and constants for thwack compression and decompression.

Key elements:
- Declares `Thwack`, `Unthwack`, `ThwBlock`, and `UnthwBlock`.
- Defines block/window sizing: `ThwMaxBlock`, encoder/decoder window blocks, compression-history block count, and hash table size.
- Defines minimum match length and match-offset coding parameters.
- Defines sequence-mask limits used to advertise history state.
- Defines encoder and decoder block structs with sequence numbers, data pointers, hash tables, acknowledgement flags, and byte limits.
- Declares public functions for initialization, compression, acknowledgement, decompression, and decoder state reporting.

Dependencies:
- Used by `thwack.c` and `unthwack.c`.

Notable behavior:
- Encoder and decoder windows are intentionally different sizes: 22 encoder blocks and 32 decoder blocks.
- `CompBlocks` limits a compressed packet to current data plus up to nine history blocks.
