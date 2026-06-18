# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcphuff.c

Progressive JPEG Huffman entropy encoder.

Key points:
- Compiled only under `C_PROGRESSIVE_SUPPORTED`.
- Maintains progressive-specific state: gather/output mode, bit buffer, DC predictors, AC table number, EOB run, buffered correction bits, restart state, derived tables, and optimization counts.
- `start_pass_phuff` selects one of four MCU encoders: DC first, AC first, DC refinement, or AC refinement; allocates correction-bit buffer for AC refinement; prepares derived tables or statistics counts.
- Output functions emit bytes with byte stuffing but do not support suspension.
- `emit_symbol`, `emit_eobrun`, and `emit_buffered_bits` abstract output vs statistics gathering.
- DC first scans encode point-transformed DC differences; AC first scans encode spectral bands with EOB run aggregation.
- DC refinement emits one refinement bit per block; AC refinement manages newly nonzero coefficients, correction bits, ZRLs, EOB runs, and buffer overflow limits.
- Finish routines flush pending EOB/bit data or generate optimized tables from gathered counts.
- `jinit_phuff_encoder` allocates encoder state and marks tables/buffers unallocated.

Dependencies and interactions:
- Shares `jpeg_make_c_derived_tbl` and `jpeg_gen_optimal_table` from `jchuff.c` via `jchuff.h`.
- Scan validity is assumed to have been checked by `jcmaster.c`.
- Used for both normal progressive compression and progressive transcoding.

Risk notes:
- Output suspension is explicitly unsupported for progressive Huffman output.
- AC refinement relies on a fixed `MAX_CORR_BITS` buffer and flush thresholds to avoid overflow.
- Right-shift handling includes portability logic for signed shifts, but coefficient coding still assumes IJG’s supported numeric ranges.
