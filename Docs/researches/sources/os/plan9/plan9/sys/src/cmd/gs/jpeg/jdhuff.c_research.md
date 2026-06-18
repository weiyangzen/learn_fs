# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.c

Purpose: sequential Huffman entropy decoder for JPEG decompression.

Key structures and routines:
- `savable_state` stores per-component DC predictors.
- `huff_entropy_decoder` stores bitreader state, restart countdown, derived DC/AC tables, per-MCU table pointers, and per-block needed flags.
- `start_pass_huff_decoder()` validates sequential scan parameters, derives Huffman tables, initializes predictors and restart state, and precomputes block-level table/need metadata.
- `jpeg_make_d_derived_tbl()` expands a public JPEG Huffman table into fast decode tables and validates table shape.
- `jpeg_fill_bit_buffer()` loads entropy-coded bytes, handles stuffed `FF/00`, detects markers, supports suspension, and pads missing data with zero bits after warning.
- `jpeg_huff_decode()` handles slow-path Huffman symbol decoding beyond the lookahead table.
- `process_restart()` consumes restart markers, resets bit state and DC predictors.
- `decode_mcu()` decodes one MCU’s DC and AC coefficients into dezigzagged natural order.
- `jinit_huff_decoder()` allocates and wires the entropy decoder.

Important behavior:
- Supports input suspension by copying permanent state into local working variables and committing only after a full MCU succeeds.
- Uses `HUFF_LOOKAHEAD` acceleration from `jdhuff.h`.
- AC values can be discarded for components or scaled outputs that do not need them.
- Corrupt/truncated entropy data degrades to warnings and zero-filled coefficients where possible.
- Restart markers reset DC predictors and bit-buffer state.

Dependencies:
- Shares bitreader and Huffman derived table declarations with `jdphuff.c` through `jdhuff.h`.
- Uses `jpeg_natural_order[]`, marker reader restart handling, source manager callbacks, and JPEG error macros.

Notes:
- This is the baseline/sequential counterpart to `jdphuff.c`.
