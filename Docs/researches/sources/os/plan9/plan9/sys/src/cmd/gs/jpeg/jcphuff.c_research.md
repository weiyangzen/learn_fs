# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcphuff.c

Progressive JPEG Huffman entropy encoder.

Key behavior:
- Compiled only under `C_PROGRESSIVE_SUPPORTED`.
- Selects separate MCU encoders for DC first scans, AC first scans, DC refinement scans, and AC refinement scans.
- Supports statistics-gathering mode for optimized Huffman table generation.
- Emits progressive AC EOBRUN symbols and buffers AC refinement correction bits.
- Handles restart markers by flushing pending EOB runs, resetting DC predictions or AC state, and emitting RST markers in output mode.
- Uses `jpeg_make_c_derived_tbl` and `jpeg_gen_optimal_table` shared with the sequential Huffman encoder.
- `jinit_phuff_encoder` installs progressive entropy callbacks and initializes table/correction-bit buffers.

Dependencies:
- Depends on validated progressive scan parameters from `jcmaster.c`.
- Uses destination manager fields directly but does not support output suspension.

Notable risks:
- Multiple-scan progressive output is incompatible with output suspension in this implementation.
- AC refinement correction buffer has a fixed `MAX_CORR_BITS` size and forces EOB emission to avoid overflow.
- DC refinement scans intentionally need no Huffman table.
