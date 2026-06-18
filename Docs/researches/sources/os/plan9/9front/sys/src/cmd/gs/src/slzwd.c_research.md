# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/slzwd.c

Implements the `LZWDecode` stream filter.

Key points:
- Uses reset, EOD, and first assignable codes derived from `InitialCodeLength`.
- Allocates a 4096-entry decode table with datum, string length, and prefix code.
- Reset initializes literal entries, special code markers, bit state, code size, and previous/copy state.
- Processing handles optional GIF-style block data, low-order or high-order bit ordering, dynamic code-size growth, reset/EOD codes, and the standard anomalous `next_code` case.
- Copies decoded strings backward through prefix chains, with suspended copy state when the output buffer fills.
- Accepts a few anomalous non-GIF files that contain one extra data item before a reset, matching Acrobat behavior.

Dependencies and interactions:
- Uses `stream_LZW_state` from `slzwx.h` and common release/defaults from `slzwc.c`.

Research relevance:
- Full LZW decompressor used for PostScript/PDF and GIF-style LZW streams.
