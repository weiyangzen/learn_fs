# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfd.c

Ghostscript `pdfwrite` path drawing implementation. It emits PDF rectangles, fills, strokes, clipping paths, and bitmap fallbacks for older PDF compatibility levels.

Key behavior:
- `gdev_pdf_fill_rectangle` skips the initial white page fill, opens page contents, clears clipping, sets fill color, and emits a rectangle fill.
- Defines `pdf_vector_procs`, adapting generic vector output with PDF-specific line width, high-level colors, rectangle clamping, and path completion behavior.
- Tracks clipping paths by ID and copied path content to avoid redundant clip emission.
- Emits clip paths from clip-path enumeration or path-list elements, including even-odd/nonzero rules.
- Rescales very large coordinates to avoid Acrobat user-coordinate limits.
- `prepare_fill_with_clip` handles empty clips, initial white-fill suppression, page/content opening, graphics-state prep, and clip output.
- Implements `pdf_lcvd_t`, a local converter backed by memory devices and optional masks.
- Converts mask bitmaps into bounded clipping paths so generated path complexity stays under `MaxClipPathSize`.
- `pdf_dump_converted_image` writes converted content as a full image, an imagemask using a pattern color, or an image clipped by a mask-derived path.
- `gdev_pdf_fill_path` handles vector fills, initial viewer-state synchronization, transparency fallback, old-PDF pattern/shading conversion, clipping, flatness, scaling, and fill operators.
- `gdev_pdf_stroke_path` handles clip setup, transparency fallback, nonuniform CTM stroke compensation, degenerate matrix workarounds, stroke clipping, line parameters, and stroke operators.
- `gdev_pdf_fill_rectangle_hl_color` handles high-level-color rectangle fills and delegates to path fill when old-PDF PatternType 2 conversion is needed.

Research notes:
- This file contains several viewer compatibility workarounds for Acrobat coordinate limits, negative line widths, singular CTMs, and old-PDF shading support.
- The local converter is shared with image handling for masked-image and shading fallbacks.
- This is rendering/output code, not filesystem functionality.
