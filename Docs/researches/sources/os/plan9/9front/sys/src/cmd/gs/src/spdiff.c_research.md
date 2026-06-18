# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spdiff.c

Implements pixel-difference encode and decode filters.

Key points:
- Supports 1-, 2-, 4-, 8-, and 16-bit components with color counts up to `s_PDiff_max_Colors`.
- Initialization computes row byte count, final-byte mask, and a switch dispatch index based on bit depth, color count, and encode/decode direction.
- Processing resets previous samples at row starts and tracks bytes left per row.
- Encoding computes current sample minus previous same-component sample; decoding computes current sample plus previous same-component sample.
- Provides specialized packed-bit loops for 1-, 2-, and 4-bit components, and byte/word loops for 8- and 16-bit components.
- Preserves unused final bits in the last row byte through `end_mask`.

Dependencies and interactions:
- Uses `spdiffx.h` state declarations.
- Implements PDF/TIFF-style predictor differencing used around compression filters.

Research relevance:
- Predictor transform for improving compression of image sample streams.
