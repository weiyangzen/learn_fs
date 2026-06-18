# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjbig2.c

Implements the `JBIG2Decode` stream filter by adapting libjbig2dec.

Key points:
- Uses external libjbig2dec heap allocation rather than full Ghostscript GC enumeration, relying on the stream release hook for cleanup.
- Error callback suppresses debug/info/warnings unless `JBIG2_DEBUG` is enabled and records fatal errors as `gs_error_ioerror`.
- `s_jbig2decode_make_global_ctx` parses a `/JBIG2Globals` byte stream into a `Jbig2GlobalCtx`, treating zero-length globals as absent.
- `s_jbig2decode_set_global_ctx` attaches parsed globals to a stream state.
- Initialization creates a jbig2 decode context using optional globals.
- Processing feeds all available input, completes the page on `last`, retrieves the single page image when available, copies bitmap bytes to output, and inverts bits because JBIG2 and PostScript use opposite black/white polarity.
- Release frees page/image and decoder context; the interpreter owns global context lifetime.

Dependencies and interactions:
- Uses `sjbig2.h`, `<jbig2.h>`, Ghostscript stream templates, and debug/error APIs.

Research relevance:
- External-library adapter for PDF 1.4 JBIG2 image streams.
