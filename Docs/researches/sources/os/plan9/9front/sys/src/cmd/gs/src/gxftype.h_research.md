# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxftype.h

Defines Ghostscript font-type and bitmap-behavior enums.

Key definitions:
- `font_type` values mirror PostScript/PDF FontType and CIDFontType dictionary values.
- Includes composite, Type 1, Type 2, user-defined, disk-based, CIDFontType 0/1/2/4, Chameleon, and TrueType Type 42.
- `fbit_type` defines bitmap behavior for ExactSize, InBetweenSize, and TransformedChar: use outlines, use bitmaps, or transform bitmaps.

Dependencies:
- None beyond base typedef/macros.

Research notes:
- These enum values are ABI-significant because they must match font dictionary values.
- Used throughout font allocation, copying, rendering, and interpretation code.
