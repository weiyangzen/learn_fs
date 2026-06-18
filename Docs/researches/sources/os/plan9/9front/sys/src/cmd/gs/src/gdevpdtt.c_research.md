# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.c

Text processing implementation for Ghostscript `pdfwrite`. This file owns the PDF text enumerator, bridges Ghostscript text enumeration to PDF text/font resources, and decides when text can be preserved as PDF text versus falling back to default rendering or Type 3 charproc accumulation.

Key behavior:
- Defines the `pdf_text_enum_t` GC descriptor and text enum procedures: resync, width-only checks, current-width forwarding, cache/setcachedevice handling, retry, release, and main `pdf_text_process`.
- `gdev_pdf_text_begin` starts pdfwrite text handling, tracks dominant text rotation for the page, rejects unsupported charpath/no-current-point cases into default text handling, and sets up special Type 3 behavior while accumulating charprocs.
- Font cache helpers attach PDF font resources to Ghostscript fonts, track glyph usage bitmaps and real-width arrays, and register font-finalization callbacks to remove cache entries.
- `pdf_font_orig_matrix` and `font_orig_scale` normalize Type 1, TrueType, CID, composite, and Type 3 font matrices for PDF width/text-matrix calculations.
- Font-resource selection checks compatible encodings, existing copied-font resources, CID system compatibility, Type 0 parent reuse, base-14 standard-font reuse, embedding eligibility, PDF version limits, CFF availability, and OPDFRead constraints.
- Builds per-text `pdf_char_glyph_pairs_t` tables so resource creation can know all used characters/glyphs and which glyphs are not already cached.
- Supports encoded text and glyphshow-style unencoded text by finding a usable PostScript encoding and rewriting glyph input into byte codes when possible.
- Marks used glyphs into resource bitsets after resource selection.
- Computes PDF text state from Ghostscript CTM, font matrix, spacing operations, current point, font size, render mode, and PDF resolution scaling.
- Writes stroke state before text state when text rendering mode uses strokes, because stroke synchronization can leave PDF text mode.
- `pdf_glyph_widths` obtains copied-font widths and original-font real widths, handles MissingWidth defaults, vertical metrics, CID v-vector compatibility, and CDevProc callouts.
- `pdf_text_process` dispatches to `process_plain_text`, `process_cid_text`, `process_cmap_text`, or `process_composite_text`, with a small aligned stack buffer and heap fallback for larger strings.
- Type 3 handling is deliberately staged: normal text processing runs until a missing glyph needs interpreter rendering, then default text processing calls BuildChar/BuildGlyph, `setcachedevice` triggers charproc attributes, the charproc is accumulated, and the glyph is processed again once widths/resources are known.
- CDevProc handling uses `TEXT_PROCESS_CDEVPROC` to let the interpreter calculate metrics, then restarts with `cdevproc_result`.

Notable dependencies:
- Text/resource layer headers: `gdevpdtx.h`, `gdevpdtd.h`, `gdevpdtf.h`, `gdevpdts.h`, `gdevpdtt.h`, `gdevpdti.h`.
- Ghostscript font/text internals: `gxfont.h`, `gxfont0.h`, `gxfcid.h`, `gxfcopy.h`, `gxfcmap.h`, `gxchar.h`, `gxstate.h`.
- PDF graphics helpers: `gdevpdfx.h`, `gdevpdfg.h`.

Research notes:
- This is PDF-generation text/font infrastructure, not filesystem code.
- The comments document several Acrobat compatibility constraints and historical Ghostscript bugs around Type 1 matrices, TrueType embedding, Type 3 clipping, and CDevProc metrics.
- `pdf_free_font_cache` currently drops the cache pointer with a FIXME about releasing elements; other removal paths free individual entries.
