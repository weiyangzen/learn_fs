# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjpx.c

Implements the `JPXDecode` stream filter by adapting the JasPer JPEG 2000 library.

Key points:
- Lets JasPer manage much of its own state while using Ghostscript non-GC memory for the temporary compressed-data buffer.
- Initialization calls `jas_init`, allocates an initial 4096-byte input buffer, and clears image/stream state.
- Because this JasPer API cannot be fed incrementally through a public stream API, the filter buffers the entire compressed input before decoding.
- `s_jpxd_buffer_input` grows the buffer by powers of two and appends incoming bytes.
- On `last`, creates a JasPer memory stream and decodes the image.
- Supports row copying for grayscale, RGB, YCbCr-to-RGB conversion, and a default multi-component path.
- Optional debug code dumps image colorspace and component metadata.
- Release destroys JasPer image/stream objects and frees the input buffer.

Dependencies and interactions:
- Uses `sjpx.h`, `<jasper/jasper.h>`, `gsmalloc.h`, and stream APIs.

Research relevance:
- External-library adapter for PDF JPX/JPEG 2000 image streams, with full-input buffering as a notable behavior.
