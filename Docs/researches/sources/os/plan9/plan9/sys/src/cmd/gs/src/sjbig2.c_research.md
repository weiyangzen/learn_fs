# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.c

JBIG2Decode stream filter adapter around the external `jbig2dec` library.

Key behavior:
- `s_jbig2decode_error` maps jbig2dec messages to Ghostscript logging and records fatal decode errors as `gs_error_ioerror`.
- `s_jbig2decode_make_global_ctx` parses a `/JBIG2Globals` byte string into a `Jbig2GlobalCtx`.
- `s_jbig2decode_set_global_ctx` attaches an externally owned global context to a stream state.
- `s_jbig2decode_init` creates an embedded-mode jbig2 decoder context using optional globals.
- `s_jbig2decode_process` feeds compressed input to jbig2dec, completes the page on final input, retrieves a page image, copies bitmap bytes out, and inverts bits to match PostScript black/white polarity.
- `s_jbig2decode_release` frees the page image and decoder context.
- Defaults clear external-library pointers for GC safety.

Notable dependencies:
- External `jbig2.h`.
- Ghostscript stream and error infrastructure.

Research notes:
- Comments explicitly bypass normal Ghostscript memory discipline for the external library and rely on `release` for cleanup.
- Several allocation paths are noted as TODO/not checked for allocation failure.
- The filter assumes a single page image.
