# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngp.c

PNGPredictorEncode/Decode stream filters implementing PNG row predictors.

Key behavior:
- Initializes bytes per row, trailing-bit mask, bytes per pixel, optional previous-row buffer, and row state.
- Supports PNG predictor algorithms: None, Sub, Up, Average, Paeth, and an `Optimum` placeholder.
- Encoding writes a predictor algorithm byte at the start of each row, then filters row bytes against left/up/upper-left references.
- Decoding reads the row predictor byte and reconstructs bytes using the corresponding inverse operation.
- Maintains `prev` bytes for left-pixel history and `prev_row` storage for Up/Average/Paeth predictors across rows.
- `paeth_predictor` implements PNG’s Paeth predictor.

Notable dependencies:
- State definition from `spngpx.h`.

Research notes:
- `optimum_predictor` is a stub that always selects Sub.
- Allocation and overflow error paths are marked “WRONG” because they return `ERRC` rather than a more specific Ghostscript error.
- The code uses Ghostscript cursor convention carefully, but the row-history memmove/copy sections are sensitive to partial buffers.
