# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpnga.c

This file is a test driver for PDF 1.4 transparency rendering to PNG. It is separate from `pngalpha` in `gdevpng.c`: it builds a custom PDF 1.4-style compositing stack and outputs RGBA PNG data from that stack.

The central data structures are `pdf14_buf` and `pdf14_ctx`. A `pdf14_buf` represents one transparency group buffer in planar layout: pixel planes, alpha, optional shape, and optional group alpha. It records isolation, knockout, group alpha/shape, blend mode, rectangle, rowstride, planestride, channel count, plane count, and data pointer. `pdf14_ctx` owns a stack of these buffers for the current page.

Buffer management includes Ghostscript GC metadata, `pdf14_buf_new/free`, `pdf14_ctx_new/free`, and group stack operations. `pdf14_push_transparency_group` creates a new buffer, optionally initializes it from the backdrop, treats knockout groups as isolated via a documented hack, and sets shape/alpha plane requirements. `pdf14_pop_transparency_group` composites the top buffer back into the saved buffer using functions from `gxblend.h`, including isolated group, recomposite group, and simplified knockout paths.

The exported device `gs_pnga_device` uses `pnga_procs`, with handlers for open, close, output_page, path fill/stroke, typed image begin, text begin, and transparency group begin/end. `pnga_open` allocates the base RGBA context. `pnga_output_page` writes the current planar RGBA buffer to a scratch file via libpng using `gp_open_scratch_file` rather than the normal `OutputFile` path; a comment notes this as a TODO.

Marking is routed through a temporary `pnga_mark_device` produced by `pnga_get_marking_device`. Path, image, and text operations are delegated to Ghostscript defaults on that marking device, whose fill-rectangle operations composite into the active PDF14 buffer. Text uses a wrapper `pnga_text_enum_t` to forward text enum operations to the target enumerator while preserving Ghostscript text state.

Filesystem relevance: only scratch-file output. This is transparency/raster compositing test infrastructure, not filesystem code.
