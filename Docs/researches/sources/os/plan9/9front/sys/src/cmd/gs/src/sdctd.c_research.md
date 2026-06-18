# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctd.c

Implements the `DCTDecode` stream filter around IJG libjpeg. It provides a JPEG source manager that suspends when more input is needed, skips pending bytes across stream chunks, and inserts a fake EOI when input ends prematurely.

The process routine is phase-driven: skip leading garbage until a marker, read headers, apply `ColorTransform` if no Adobe marker overrides it, start decompression, stream scanlines to output, optionally buffer oversized scanlines, finish decompression, and return EOFC.

Dependencies include `jpeglib_.h`, `jerror_.h`, `sdct.h`, `sjpeg.h`, Ghostscript memory/debug headers, and IJG decompression APIs via Ghostscript wrappers.

Risk notes: fake EOI tolerance is compatibility behavior. Release destroys JPEG state and frees scanline/decompress allocations.
