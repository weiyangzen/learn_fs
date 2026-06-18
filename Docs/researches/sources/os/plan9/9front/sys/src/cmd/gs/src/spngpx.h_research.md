# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spngpx.h

Defines PNG predictor filter state.

Key points:
- `stream_PNGP_state` stores colors, bits per component, columns, predictor choice, row byte count, end mask, bytes per pixel, previous-row pointer, dispatch index, row progress, and previous-sample bytes.
- Defaults are 1 color, 8 bits/component, 1 column, predictor 15, and no previous-row allocation.
- GC descriptor traces the allocated previous-row buffer.
- Declares PNG predictor encode/decode templates.

Research relevance:
- State/API header for PNG predictor filters.
