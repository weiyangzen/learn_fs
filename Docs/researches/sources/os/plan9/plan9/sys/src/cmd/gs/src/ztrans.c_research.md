# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrans.c

## Purpose
Implements PostScript/PDF transparency operators for blend mode, alpha, text knockout, transparency groups, soft masks, ImageType 3x masks, and pdf14 device-filter management.

## Public Surface
Registered in split tables:
- `ztrans1_op_defs`: `.setblendmode`, `.currentblendmode`, `.setopacityalpha`, `.currentopacityalpha`, `.setshapealpha`, `.currentshapealpha`, `.settextknockout`, `.currenttextknockout`.
- `ztrans2_op_defs`: `.begintransparencygroup`, `.discardtransparencygroup`, `.endtransparencygroup`, `.begintransparencymaskgroup`, `.begintransparencymaskimage`, `.discardtransparencymask`, `.endtransparencymask`, `.inittransparencymask`, `.image3x`, `.pushpdf14devicefilter`, `.poppdf14devicefilter`.

## Implementation Notes
- Float getter/setter helpers abstract alpha accessors.
- `enum_param` maps name refs to blend/mask subtype indexes.
- Transparency group setup reads `Isolated`, `Knockout`, current color space, and bounding box coordinates.
- Mask group setup reads subtype, background/gray background, optional transfer function, and bbox.
- `tf_using_function` bridges Ghostscript functions to mask transfer functions.
- `.image3x` reads `DataDict` and optional `ShapeMaskDict`/`OpacityMaskDict`, validates interleave/data-source rules, and inserts mask data sources before image data as needed.
- pdf14 filter push/pop operators delegate to `gs_push_pdf14trans_device` and `gs_pop_pdf14trans_device`.

## Dependencies
Touches graphics state, color spaces, image parameter parsing, dictionaries, functions, transparency graphics library, and pdf14 device support.

## Risks and Notes
- Mask dictionary validation is subtle: interleave type must agree with available data sources.
- Transfer functions must be single-input/single-output functions.
- `.discard*` operators require current transparency layer type checks.
- Filesystem relevance: none directly; rendering/transparency pipeline only.
