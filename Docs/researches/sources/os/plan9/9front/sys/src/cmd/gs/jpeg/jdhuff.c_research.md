# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.c

Sequential Huffman entropy decoder and shared Huffman table/bit-buffer routines.

Key points:
- Maintains bit-buffer state and DC prediction state so suspension can roll back to the start of the current MCU.
- `start_pass_huff_decoder` validates sequential scan parameters, derives active DC/AC Huffman tables, resets predictors, and precomputes per-block table and needed-coefficient flags.
- `jpeg_make_d_derived_tbl` validates Huffman code lengths, builds canonical decode tables, fills lookahead entries, and validates DC symbols.
- `jpeg_fill_bit_buffer` reads stuffed entropy bytes, detects markers, inserts zero bits after early segment termination, and preserves suspension state.
- `jpeg_huff_decode` handles slow-path over-lookahead Huffman decoding and returns a safe zero on corrupted overlong codes.
- `decode_mcu` decodes DC differences and AC run-length symbols into natural-order coefficients, or discards values for unneeded AC/DC paths.
- Restart processing discards unused bits, reads/recovers restart markers, resets DC predictors, and refreshes restart counters.

Dependencies and interactions:
- Shares `jdhuff.h` helpers with progressive Huffman decoding in `jdphuff.c`.
- Called by `jdcoefct.c` through the entropy decoder interface.
- Uses marker-reader restart handling from `jdmarker.c`.

Risk notes:
- Corrupt entropy data is often converted to warnings plus gray/zero-filled output rather than fatal errors.
- AC decoding relies on the padded `jpeg_natural_order` table to tolerate corrupted run lengths.
- Suspension correctness depends on only committing bit/source and predictor state after a complete MCU.
