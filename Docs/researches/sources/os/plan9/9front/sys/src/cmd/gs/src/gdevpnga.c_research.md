# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpnga.c

Experimental/test Ghostscript PNG alpha driver for PDF 1.4 transparency. It maintains a planar RGBA transparency stack, composites groups with `gxblend` helpers, and writes the final result as a scratch PNG.

Key behavior:
- Defines `pdf14_buf`, a planar buffer with saved-stack pointer, isolated/knockout flags, group alpha/shape, blend mode, rectangle, row/plane strides, channel/plane counts, and backing data.
- Defines `pdf14_ctx`, which owns the current buffer stack, allocator, page rectangle, and channel count.
- Defines the `pnga` device and a transient `pnga_mark` device used for actual marks under the current imager state's opacity, shape, and blend mode.
- `pdf14_buf_new`, `pdf14_buf_free`, `pdf14_ctx_new`, and `pdf14_ctx_free` allocate and release planar transparency buffers.
- `pdf14_push_transparency_group` creates a new group buffer, forces knockout groups isolated as a simplifying hack, copies backdrop data when needed, and records group compositing parameters.
- `pdf14_pop_transparency_group` composites the top group into its parent using `art_pdf_composite_group_8`, `art_pdf_recomposite_group_8`, or knockout helpers, updating alpha/shape planes as needed.
- `pnga_open` creates a 4-channel PDF 1.4 context for the whole page; `pnga_close` frees it.
- `pnga_output_page` writes the current top buffer as 8-bit RGBA PNG through libpng, but opens a scratch file with `gp_open_scratch_file` rather than using the normal printer `OutputFile`.
- `pnga_get_marking_device` copies a `pnga_mark` device, wires it to the parent context, captures opacity/shape/blend mode, and selects normal or simple-knockout rectangle marking.
- `pnga_fill_path`, `pnga_stroke_path`, `pnga_begin_typed_image`, and `pnga_text_begin` render through temporary marking devices so normal Ghostscript high-level rendering eventually lands in `pnga_mark_fill_rectangle` paths.
- Text support wraps a target text enumerator and forwards process/resync/width/cache/retry/release calls.
- `pnga_begin_transparency_group` and `pnga_end_transparency_group` push and pop PDF 1.4 transparency groups.
- `pnga_mark_fill_rectangle` and `pnga_mark_fill_rectangle_ko_simple` composite colored rectangles into the current planar RGBA buffer, including alpha-g and shape planes when present.

Notable dependencies:
- Ghostscript printer/device/text/memory APIs: `gdevprn.h`, `gsdevice.h`, `gdevmem.h`, `gxtext.h`.
- PDF 1.4 blending helpers from `gxblend.h`.
- libpng through `png_.h`.

Research notes:
- The file labels itself as a test driver; it is not a general production PNG device.
- `pnga_output_page` contains a TODO noting it should use `OutputFile` rather than a scratch file.
- `pdf14_ctx_new` allocates `result` and then calls `pdf14_buf_new` before checking whether `result` is null; a failed context allocation followed by a successful buffer allocation would dereference null later.
- In both rectangle marking routines, the y lower-bound clamp checks `y < buf->rect.p.x` rather than `y < buf->rect.p.y`, which looks like a coordinate typo.
- Group handling deliberately treats all knockout groups as isolated, which the comment says is not fully correct.
