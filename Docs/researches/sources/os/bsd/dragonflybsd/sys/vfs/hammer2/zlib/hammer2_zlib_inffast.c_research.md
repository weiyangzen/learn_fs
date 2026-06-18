# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inffast.c

Fast inflate inner-loop decoder for HAMMER2’s vendored zlib decompressor.

Key responsibilities:
- Implements `inflate_fast()`, the hot path for decoding deflate literal/length and distance codes.
- Decodes literals, length/distance pairs, second-level Huffman table entries, and end-of-block markers.
- Copies match data either from the current output buffer or from the sliding window.
- Detects invalid literal/length codes, invalid distance codes, and invalid distances too far back.
- Updates `z_stream` pointers/counters and inflate bit buffer state before returning to the main inflate state machine.

Important implementation details:
- The routine assumes it is entered in `LEN` mode with at least six input bytes, at least 258 output bytes, and fewer than eight held bits.
- Localizes stream/state fields for speed, including input/output pointers, window position, bit accumulator, Huffman tables, and masks.
- Supports pre-increment vs post-increment pointer tuning through `POSTINC`.
- A length/distance pair can consume up to 48 bits and output up to 258 bytes, which drives the entry assumptions.
- On end-of-block it sets mode to `TYPE`; on invalid data it sets mode to `BAD` and stores a message.
- Handles wrapped-window copies through `wnext`, `whave`, and `wsize`, then finishes any remaining copy from already-produced output.
- Restores unused input bytes by rolling back whole bytes from the bit accumulator before updating stream fields.

Dependencies:
- Includes zlib utility, inflate tree, inflate state, and inffast headers.
- Called by the main inflate implementation when buffer sizes allow the fast path.

Notable risks:
- Entry preconditions are strict; calling with insufficient input/output space can overrun assumptions.
- Distance-copy logic is intricate around window wraparound and overlap; small changes can corrupt decompressed output.
- Strict distance checking depends on `INFLATE_STRICT` and `state->sane`; compatibility modes may permit invalid-distance recovery behavior if enabled.
- The function mutates mode and error message directly, so callers must resume the main inflate state machine correctly.
