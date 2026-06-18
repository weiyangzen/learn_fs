# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2eps.c

PostScript/PDF-side JPEG translator.

Key function:

- `bTranslateJPEG()` seeks to the JPEG payload, emits image prologue, ASCII85-encodes the JPEG bytes to the output file, then emits image epilogue.

Debug-only helper:

- `vCopy2File()` can dump embedded JPEGs into `/tmp/pic/picNNNN.jpg` when compiled with `DEBUG`.

The module does not decode JPEG pixels; it wraps already-validated JPEG data for EPS-style output. Actual prologue/epilogue behavior is delegated through generic output functions.
