# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.c

THWACK encoder implementation, a compact LZ77-like compressor with acknowledged history windows.

Key behavior:
- `thwackinit()` resets hash/history slots and frees retained blocks.
- `thwackcleanup()` frees retained encoder blocks.
- `thwackack()` marks transmitted history blocks as safe for future references based on a sequence number and bitmask.
- `thwack()`:
  - Adds the current source block into the encoder window.
  - Builds a history set from recently acknowledged blocks.
  - Emits sequence delta and history mask.
  - Finds repeated strings through per-block hash tables.
  - Encodes literals with adaptive literal history and matches with variable-length length/offset codes.
  - Rejects output when it is larger than the destination unless `mustadd` forces dictionary insertion.

Integration:
- Used by `thw.c` as the PPP compressor.
- Uses `Block` ownership: the compressor retains successful source blocks in `tw->data`.

Risks and notes:
- Compression assumes source blocks are at most `ThwMaxBlock`.
- `mustadd` can cause dictionary insertion even when output is not useful.
- Retained `Block*` ownership is subtle and must align with PPP block lifetime.
