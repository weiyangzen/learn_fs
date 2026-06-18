# File Research: sources/os/plan9/plan9/sys/src/9/port/thwack.c

Implements the Thwack LZ77/Huffman-style compressor.

Core structures and constants:
- Uses `Thwack`, `ThwBlock`, and constants from `thwack.h`.
- Local `Huff` table `lentab` encodes short match lengths.
- Maintains an encoder window of acknowledged blocks and per-block hash tables.

Key functions:
- `thwackinit` clears compressor state and initializes block data/hash pointers.
- `thwackack` marks a block sequence and selected predecessor blocks as acknowledged for future history use.
- `thwmatch` searches current/history blocks for a match using hashed 3-byte sequences and returns an offset into history.
- `thwack` compresses one source block:
  - Adds source to the circular window.
  - Builds a history list from acknowledged recent blocks.
  - Writes sequence-delta and history mask prefix.
  - Emits literal codes or match length/offset codes.
  - Updates hash entries as source advances.
  - Aborts with `-1` if data is too small/large, output would not fit, or compression progress is poor.
  - Updates stats for input bytes, output bytes, literals, matches, offset bits, length bits, delay, and history.

Important behavior:
- Only acknowledged previous blocks are used as compression history, making it suitable for lossy/unreliable transport contexts where receiver history must be known.
- Hash uses Knuth-style multiplicative hashing over 3-byte values.
- Literal encoding adapts based on recent literal history to vary 8/9/10/11-bit forms.
- Match length uses fast table for short matches and expanding big-length encoding for longer ones.

Role:
- Portable compression helper, likely used by network or remote display/file protocols in this tree.
