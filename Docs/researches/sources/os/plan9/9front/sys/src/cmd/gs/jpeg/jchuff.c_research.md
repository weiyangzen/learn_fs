# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.c

Sequential Huffman entropy encoder plus optimal Huffman table generator.

Key points:
- Maintains savable bit/DC predictor state so output suspension can roll back to the start of an MCU.
- `start_pass_huff` selects real encoding or statistics-gathering mode, prepares derived tables or count arrays, resets DC predictors, bit buffer, and restart state.
- `jpeg_make_c_derived_tbl` validates a `JHUFF_TBL`, derives canonical Huffman codes and sizes, rejects illegal/duplicate symbols, and fills `c_derived_tbl`.
- `encode_one_block` emits DC difference category/value bits and AC run-length/category/value symbols, including ZRL and EOB handling.
- `encode_mcu_huff` handles restart markers, encodes each block in the MCU, commits destination and predictor state only after the MCU succeeds, and updates restart counters.
- `finish_pass_huff` flushes pending bits.
- With `ENTROPY_OPT_SUPPORTED`, gather mode counts symbols and `jpeg_gen_optimal_table` builds length-limited canonical Huffman tables using JPEG section K.2-style adjustment.
- `finish_pass_gather` generates updated DC/AC tables once per used table.

Dependencies and interactions:
- Includes `jchuff.h`, sharing derived-table declarations and `MAX_COEF_BITS` with progressive Huffman.
- Called by `jccoefct.c`/`jctrans.c` through the entropy encoder interface.
- Marker emission uses restart marker constants and byte-stuffing rules.

Risk notes:
- Negative coefficient coding assumes two’s complement behavior, as comments state.
- Optimization mutates frequency arrays while generating tables; callers prevent multiple generation passes per table.
- Suspension support depends on destination managers respecting `next_output_byte`/`free_in_buffer` rollback semantics.
