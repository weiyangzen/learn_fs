# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.c

## Role

`gdevpdtt.c` is the main pdfwrite text-processing implementation. It bridges Ghostscript text enumeration to PDF text/font resources, choosing whether text can be represented directly in PDF or must fall back to the default renderer.

## Main Entry Points

- `gdev_pdf_text_begin()` creates `pdf_text_enum_t`, tracks page text rotation, handles stringwidth special cases, and decides whether pdfwrite text handling can start.
- `pdf_text_process()` is the enumerator process function. It dispatches text to CID, CMap/composite, or plain text processors, manages fallback to default rendering, and handles Type 3 charproc accumulation and CDevProc restart behavior.
- `pdf_default_text_begin()` wraps fallback default text processing, forcing real drawing for Type 3 charproc accumulation when needed.

## Font Resource Flow

- `pdf_obtain_font_resource()`, `pdf_obtain_font_resource_unencoded()`, and `pdf_obtain_cidfont_resource()` find or allocate compatible font resources and mark glyph usage.
- `pdf_find_font_resource()` and `pdf_find_type0_font_resource()` search existing resource chains for reusable font resources by type, encoding compatibility, CMap name, descendant font, and copyable glyph outlines.
- `pdf_make_font_resource()` creates standard, simple, CID, TrueType, CFF, or Type 3 font resources, including embed-policy checks and PDF-version/CID-system capability checks.
- `pdf_make_font3_resource()` creates synthesized Type 3 resources with cached glyph state, base encoding, font bbox, and adjusted FontMatrix precision.
- `pdf_attach_font_resource()` stores resource associations in a device font cache and registers font-removal notification callbacks.

## Text And Glyph State

- `pdf_char_glyph_pairs_t` tables are allocated per text run to record all glyph/code pairs and the unused glyphs needing copy or embedding.
- `pdf_make_text_glyphs_table()` scans encoded text through `next_char_glyph`; `pdf_make_text_glyphs_table_unencoded()` rewrites glyphshow data into a compatible known PostScript encoding.
- `pdf_mark_text_glyphs()` and `pdf_mark_text_glyphs_unencoded()` update per-font glyph usage bitmaps.
- `pdf_text_release_cgp()` frees per-enumerator glyph-pair storage.

## Coordinate And Width Handling

- `pdf_font_orig_matrix()` reconstructs the original font matrix, including Type 1/TrueType/CID special cases and heuristics for scaled Type 1 fonts.
- `pdf_update_text_state()` computes PDF text state values from font matrices, the Ghostscript CTM, text current point, spacing deltas, render mode, and selected PDF font.
- `pdf_set_text_process_state()` emits stroke/text state updates, taking care that stroke setup may leave text mode.
- `pdf_glyph_widths()` obtains both copied-font widths for PDF Widths arrays and original-font widths for rendering, including missing-width fallback, vertical metrics, CID v-vector compatibility, and CDevProc callouts.

## Fallback And Type 3 Accumulation

The file has intricate Type 3 behavior. `pdf_text_process()` may render until a glyph cannot be copied, then fall back to default interpretation so BuildChar/BuildGlyph can execute. `pdf_text_set_cache()` captures `setcharwidth` / `setcachedevice` data, starts or cancels charproc resource accumulation, installs clipping needed by the interpreter fallback, and resumes the normal text pass once widths and charproc attributes are known.

## Dependencies

This file depends on Ghostscript text, font, CMap, glyph, matrix, path, graphics-state, resource, PDF output, font descriptor, bitmap font, and high-level device APIs. It calls implementation layers declared in `gdevpdtt.h`, including `process_plain_text()`, `process_cid_text()`, `process_cmap_text()`, and `process_composite_text()`.

## Risks And Invariants

- Correctness depends on preserving the relationship between current font, original font, copied font, glyph usage, and PDF resource encoding.
- Type 3 fallback is intentionally two-pass: first to execute charproc/cache callbacks, second to emit text with known metrics.
- CDevProc handling relies on restarting with `cdevproc_result` rather than requerying font metrics.
- `pdf_free_font_cache()` only nulls the cache root and has a FIXME about releasing elements, so lifetime ownership is external or intentionally leaky at close time.
- Encoding compatibility is conservative and may reject reusable resources if glyph/name mappings conflict.
