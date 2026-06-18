# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdphuff.c

Progressive Huffman entropy decoder.

Key points:
- Compiled under `D_PROGRESSIVE_SUPPORTED`; otherwise the file contributes no decoder implementation.
- Extends savable entropy state with `EOBRUN` plus per-component DC predictors, preserving suspension rollback at MCU boundaries.
- `start_pass_phuff_decoder` validates progressive scan parameters, warns on suspect progression order, updates `coef_bits`, selects the scan-specific decode routine, and derives required Huffman tables.
- Supports four decode paths: DC first, AC first, DC refinement, and AC refinement.
- DC first decodes differences and writes coefficients shifted by `Al`; DC refinement ORs in the next approximation bit.
- AC first handles spectral bands, zero runs, and EOB runs, writing natural-order coefficients shifted by `Al`.
- AC refinement appends correction bits to existing coefficients and records newly nonzero coefficients so it can undo them if suspension occurs mid-MCU.
- Restart handling clears bit state, DC predictors, EOB runs, and restart counters.
- `jinit_phuff_decoder` allocates derived-table slots and initializes the per-component coefficient progression table to unknown.

Dependencies and interactions:
- Shares derived Huffman table and bit-buffer helpers with `jdhuff.c` through `jdhuff.h`.
- Requires full coefficient buffering in `jdcoefct.c` for progressive scans.

Risk notes:
- Bogus progression is mostly warned about rather than fatal, except invalid scan parameter structure.
- Large `Al` values are accepted liberally and may produce odd output rather than crashing.
- AC refinement is especially sensitive to suspension because newly nonzero coefficients alter later decoding semantics.
