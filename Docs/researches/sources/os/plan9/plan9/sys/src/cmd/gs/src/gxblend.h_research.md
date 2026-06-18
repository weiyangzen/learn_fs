# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.h

Purpose: Declares PDF transparency blending and compositing APIs implemented in `gxblend.c`.

Key definitions:
- `ArtPixMaxDepth` is `bits16`.
- `ART_MAX_CHAN` is 16.

Declared API:
- Pixel blending: `art_blend_pixel()`, `art_blend_pixel_8()`.
- Alpha union: `art_pdf_union_8()`, `art_pdf_union_mul_8()`.
- Basic compositing: `art_pdf_composite_pixel_alpha_8()`.
- Group operations: `art_pdf_uncomposite_group_8()`, `art_pdf_recomposite_group_8()`, `art_pdf_composite_group_8()`.
- Knockout operations: `art_pdf_composite_knockout_simple_8()`, `art_pdf_composite_knockout_isolated_8()`, `art_pdf_composite_knockout_8()`.

Behavior:
- Documents that implementations are reference-oriented rather than high performance.
- States that subtractive color spaces such as CMYK should pass complemented pixel values.
- Requires pixel buffers to be aligned/padded enough that 32-bit copying may access bytes through `[(n_chan + 3) & -4]`.

Dependencies:
- Requires `bits16`, `byte`, and `gs_blend_mode_t`.

Notable risks:
- API leaves Compatible blend mode semantically unresolved in comments.
