# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.h

Declares PDF transparency blending and compositing routines.

Key definitions:
- `ArtPixMaxDepth` is a 16-bit channel type; `ART_MAX_CHAN` limits stack blend buffers to 16 channels.
- Declares 16-bit and 8-bit blend functions over arbitrary channel counts.
- Declares alpha-union helpers for plain and mask-scaled union.
- Declares 8-bit source-over alpha compositing, group uncompositing/recompositing, isolated-group compositing, and knockout compositing variants.

Research notes:
- The API documentation states that subtractive spaces such as CMYK must be represented as complemented values before blending.
- Several functions assume a single alpha channel and 32-bit-aligned pixel buffers, with bytes beyond channel count potentially accessed by fast copies.
