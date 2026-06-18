# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spngp.c

Implements PNG predictor encode and decode filters.

Key points:
- Supports PNG predictors None, Sub, Up, Average, Paeth, and a placeholder optimum predictor that currently returns Sub.
- Initialization computes row byte count, bits-per-pixel byte count, final-byte mask, and optionally allocates a previous-row buffer.
- Encoding writes a predictor algorithm byte at the start of each row and then emits filtered row data.
- Decoding reads the row predictor byte and reconstructs bytes using the selected filter.
- `s_pngp_process` contains common encode/decode arithmetic for None/Sub/Up/Average/Paeth.
- Maintains `prev` for bytes before the current position and `prev_row` for vertical predictors across partial stream calls.
- Release frees the previous-row buffer.

Dependencies and interactions:
- Uses `spngpx.h` state declarations.
- Implements PNG predictor logic used by PDF filter pipelines.

Research relevance:
- Row predictor transform for PNG/PDF image compression streams.
