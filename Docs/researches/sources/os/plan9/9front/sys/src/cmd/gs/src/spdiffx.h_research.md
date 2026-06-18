# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spdiffx.h

Defines pixel-difference filter state.

Key points:
- Sets `s_PDiff_max_Colors` to 16.
- `stream_PDiff_state` stores client parameters (`Colors`, `BitsPerComponent`, `Columns`), computed row metadata, switch dispatch index, row progress, and previous samples.
- Defaults are 1 color, 8 bits/component, and 1 column.
- Declares encode and decode templates.

Research relevance:
- State/API header for pixel-difference predictor filters.
