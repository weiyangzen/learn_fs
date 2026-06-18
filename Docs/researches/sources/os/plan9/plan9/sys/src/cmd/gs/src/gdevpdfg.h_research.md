# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.h

Internal graphics interface header for the Ghostscript `pdfwrite` driver. It gathers declarations shared by color-space, graphics-state, image, pattern, and bitmap-copy modules.

Key contents:
- Defines full and abbreviated PDF color-space name sets.
- Defines `pdf_color_space_t`, a PDF resource subclass carrying range-scaling data plus serialized color-space bytes for deduplication.
- Declares Device-space initialization, generic/named PDF color-space conversion, Pattern color spaces, and image ProcSet updates.
- Declares graphics-state functions for viewer-state copy/reset, initial colors, color setting, drawing preparation, viewer save/restore, ExtGState finalization, and COS-name conversion.
- Defines `pdf_pattern_t` with a `substitute` pointer for deduplicated pattern resources.
- Defines image dictionary name sets and `pdf_image_writer`, including support for up to four alternative writer streams.
- Declares image matrix, XObject, bitmap-copy, filter, compression-choice, and charproc-resource helpers.
- Declares PatternType 1 storage and colored/uncolored/shading pattern color emission hooks.

Research notes:
- This is a private cross-module contract, organized by the implementation file that exports each group.
- The image writer supports primary image data, alternative compression, compression chooser, and optional mask streams.
- It exposes no filesystem interfaces.
