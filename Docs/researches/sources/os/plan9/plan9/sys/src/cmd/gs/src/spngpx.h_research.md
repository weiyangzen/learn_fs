# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngpx.h

Header for PNGPredictor encode/decode filters.

Key contents:
- Defines `stream_PNGP_state` with predictor parameters, computed row size/mask/bytes-per-pixel, previous-row pointer, dispatch index, row bytes left, and previous sample bytes.
- Default parameters: 1 color, 8 bits/component, 1 column, predictor 15.
- Declares GC pointer tracing for `prev_row` and encode/decode stream templates.

Notable dependencies:
- Requires stream implementation context from `strimpl.h`.

Research notes:
- `prev` is fixed at 32 bytes, sufficient for documented `Colors` 1..16 with up to 16 bits/component.
