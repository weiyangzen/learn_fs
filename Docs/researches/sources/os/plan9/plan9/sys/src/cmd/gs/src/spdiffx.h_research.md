# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiffx.h

Header for PixelDifference encode/decode filters.

Key contents:
- Defines `s_PDiff_max_Colors` as 16.
- Defines `stream_PDiff_state` with client parameters (`Colors`, `BitsPerComponent`, `Columns`), computed row metadata, dispatch index, row bytes left, and previous samples.
- Provides default parameters: 1 color, 8 bits/component, 1 column.
- Declares encode and decode stream templates.

Notable dependencies:
- Requires stream implementation context from `strimpl.h`.

Research notes:
- The comment says `BitsPerComponent` supports 1, 2, 4, 8, while the implementation also contains 16-bit cases; this mismatch is worth checking before using 16-bit mode.
