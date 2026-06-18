# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfd.c

Ghostscript `pdfwrite` path drawing implementation. It emits PDF rectangle, fill, stroke, clipping, and older-PDF shading fallback output from Ghostscript vector drawing calls.

Key behavior:
- `gdev_pdf_fill_rectangle` suppresses the initial white page fill, opens page contents, clears clipping, sets fill color, and emits a PDF `re f` rectangle.
- Defines `pdf_vector_procs`, adapting generic `psdf` vector output with PDF-specific line width normalization, high-level fill/stroke color setting, rectangle clipping/clamping, and path completion.
- Tracks clipping paths by ID and by copied path content to avoid redundant clip emission; restores/saves viewer graphics state with `Q`/`q` when replacing active clips.
- Emits clipping paths from regular clip-path enumeration or from path-list elements, including reverse path-list order and even-odd/nonzero clipping rules.
- `make_rect_scaling` and the fill/stroke paths rescale very large coordinates to stay within Acrobat user-coordinate limits.
- `prepare_fill_with_clip` handles empty clips, skipped initial white fills, page/content opening, graphics-state preparation, and clip emission.
- Implements a local converter device (`pdf_lcvd_t`) backed by memory devices and optional masks for converting unsupported shadings/masked images into image or imagemask output.
- Converts mask bitmaps into clipping paths in bounded subimages so generated clip path complexity stays under `MaxClipPathSize`.
- `pdf_dump_converted_image` writes converted content either as a full image, an imagemask using a pattern color, or an image clipped by a bitmap-derived path.
- `gdev_pdf_fill_path` handles ordinary vector fills, initial graphics-state synchronization hacks, transparency fallback, pattern/shading conversion for PDF 1.2 compatibility, clipping intersections, flatness updates, path scaling, and `f`/`f*` fill operators.
- `gdev_pdf_stroke_path` handles clip setup, transparency fallback, nonuniform CTM stroke compensation, Acrobat matrix edge cases, stroke-bounds intersection with the clip box, line-parameter preparation, and `S`/`s` output.
- `gdev_pdf_fill_rectangle_hl_color` implements high-level-color rectangle filling and delegates to the path fill path when old-PDF pattern2 conversion is needed.

Notable dependencies:
- Ghostscript geometry/path/clip/imager internals: `gxfixed.h`, `gxistate.h`, `gxpaint.h`, `gxcoord.h`, `gzpath.h`, `gzcpath.h`, `gxdevmem.h`.
- PDF graphics/color/image helpers from `gdevpdfx.h`, `gdevpdfg.h`, and `gdevpdfo.h`.
- Uses `pdf_copy_color_data` from image-writing support to turn memory-device raster content into PDF images.

Research notes:
- This file encodes several PDF viewer compatibility workarounds, especially Acrobat coordinate limits, negative line widths, and singular/degenerate CTM behavior.
- The `pdf_lcvd_t` converter is shared with image handling and is central to compatibility fallback for masked images and shadings that cannot be represented directly.
- Several comments describe intentional hacks required by Ghostscript’s pdfmark/high-level rendering interface, such as empty-path fills for initial state and clipping synchronization.
- This is rendering/output code, not filesystem functionality.
