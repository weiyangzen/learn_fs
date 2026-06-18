# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/whack.c

Purpose: Custom LZ77-style compressor used by Venti.

Key behavior:
- `whackinit` sizes the hash-chain search limit from the compression level and initializes the dictionary state.
- `whackmatch` searches recent dictionary entries for a match within `WhackMaxOff`.
- `whack` emits literals or length/offset matches using variable-length encodings and updates compression statistics.
- Bails out when compression is disabled, input too small, output would exceed input size, or poor compression progress is detected.
- `whackblock` compresses one block with default level 6.

Dependencies:
- Uses structures/constants from `whack.h`; paired with `unwhack.c`.

Notable details:
- Match offset is limited to 16 KiB.
- `compressblocks` is a global switch.
