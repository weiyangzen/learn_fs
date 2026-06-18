# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.h

Internal graphics interface header for the Ghostscript `pdfwrite` driver. It gathers declarations shared by color-space, graphics-state, image, pattern, and bitmap-copy modules.

Key contents:
- Defines full and abbreviated PDF color-space name sets and the `pdf_color_space_names_t` structure.
- Defines `pdf_color_space_t`, a PDF resource subclass that retains CIE range scaling data plus serialized color-space bytes for deduplication.
- Declares color-space creation functions: Device-space initialization, generic/named PDF color-space conversion, Pattern color spaces, and image ProcSet updates.
- Declares graphics-state functions from `gdevpdfg.c`: viewer-state copy/reset, initial colors, pure/high-level color setting, drawing/fill/stroke/image/imagemask preparation, viewer save/restore, ExtGState finalization, and string-to-COS-name conversion.
- Defines `pdf_pattern_t`, a resource wrapper with a `substitute` pointer for deduplicated pattern resources, and declares `pdf_substitute_pattern`.
- Defines image dictionary name sets, `pdf_image_writer`, its GC descriptor, and image-writing helper declarations used by `gdevpdfi.c`, `gdevpdfj.c`, and bitmap copy paths.
- Declares PatternType 1 parameter storage and colored/uncolored/shading pattern color emission from `gdevpdfv.c`.
- Declares `pdf_copy_color_data`, the bitmap-to-PDF-image helper exported by the bitmap/copy code.

Research notes:
- The header is a cross-module private contract for the PDF-writing device; many declarations are intentionally grouped by the implementation file that exports them.
- `pdf_image_writer_num_alt_streams` is `4`, covering main image data, an alternative compression stream, a compression chooser stream, and optional mask stream.
- The resource descriptors are public/private through Ghostscript GC macros because resource objects need tracing/relocation across modules.
- The file exposes no filesystem interfaces.
