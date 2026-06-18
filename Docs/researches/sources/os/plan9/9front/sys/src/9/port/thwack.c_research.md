# File Research: sources/os/plan9/9front/sys/src/9/port/thwack.c

Thwack encoder: compact LZ77-style block compressor with acknowledged history-window support.

Key responsibilities:
- Initializes encoder block windows and per-block hash tables.
- Records acknowledgements so only decoder-known history blocks are used for compression.
- Builds a history list from current block plus recently acknowledged predecessor blocks.
- Uses multiplicative hashing over three-byte sequences to find candidate matches.
- Encodes literals with adaptive literal history and encodes matches as length plus history offset.
- Emits sequence-delta and mask bytes so the decoder can reconstruct the history set.
- Tracks compression statistics: input bytes, output bytes, literals, matches, offset bits, length bits, delay, and history.
- Rejects blocks that are too large, too small, output larger than input buffer, or insufficiently compressible midway.

Dependencies:
- Uses definitions and window structures from `thwack.h`.

Notable behavior:
- Current source block is copied into the encoder window before compression.
- The encoder only uses acknowledged history blocks, preventing references to data the decoder may not have.
- Match length and offset use custom variable-length coding tables, not a generic Huffman tree despite the local `Huff` table name.
