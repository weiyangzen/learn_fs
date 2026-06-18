# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdphuff.c

Purpose: progressive JPEG Huffman entropy decoder.

Key structures and routines:
- `savable_state` stores `EOBRUN` plus DC predictors.
- `phuff_entropy_decoder` stores bitreader state, restart countdown, derived tables, and active AC table.
- `start_pass_phuff_decoder()` validates progressive scan parameters, updates coefficient progression status, selects the MCU decode routine, derives tables, and initializes restart/bit state.
- `process_restart()` handles RST markers, resets DC predictors and EOB run count.
- `decode_mcu_DC_first()` decodes initial DC scans.
- `decode_mcu_AC_first()` decodes initial AC spectral scans with EOB run handling.
- `decode_mcu_DC_refine()` appends one refinement bit to DC coefficients.
- `decode_mcu_AC_refine()` handles AC successive approximation, including correction bits, new nonzero coefficients, EOB runs, and rollback on suspension.
- `jinit_phuff_decoder()` allocates the decoder and progression-status table `coef_bits`.

Important behavior:
- Compiled only under `D_PROGRESSIVE_SUPPORTED`.
- AC scans must contain exactly one component; DC scans may be multi-component.
- Scan order inconsistencies are warnings, while invalid scan parameters are fatal.
- AC refinement must undo newly nonzero coefficients if input suspension occurs mid-MCU, because future decoding depends on zero/nonzero state.
- Reuses Huffman bitreader and derived table machinery from `jdhuff.c`/`jdhuff.h`.

Dependencies:
- Requires coefficient buffers from the progressive coefficient controller path.
- Uses `jpeg_natural_order[]`, marker restart handling, error macros, and source-manager suspension semantics.

Notes:
- This is the progressive counterpart to `jdhuff.c`, with additional complexity for spectral selection and successive approximation.
