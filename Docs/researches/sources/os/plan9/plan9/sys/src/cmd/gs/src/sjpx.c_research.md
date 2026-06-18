# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.c

JPXDecode/JPEG 2000 stream filter adapter around the external JasPer library.

Key behavior:
- `s_jpxd_init` initializes JasPer, allocates a temporary compressed-data buffer, and chooses non-GC memory for external-library objects.
- Optional debug code dumps decoded image geometry, colorspace, components, precision, signedness, and subsampling.
- Row-copy helpers emit gray, RGB, YCbCr-to-RGB, or generic component data from a JasPer image into Ghostscript output buffers.
- `s_jpxd_buffer_input` spools all compressed input into a growable buffer because the code does not feed JasPer incrementally.
- `s_jpxd_decode_image` wraps the buffer in a JasPer memory stream, decodes the image, optionally converts multicomponent non-RGB images to sRGB, and closes the JasPer stream.
- `s_jpxd_process` buffers input until `last`, decodes on demand, and outputs one row fragment at a time.
- `s_jpxd_release` frees JasPer image/stream resources and the temporary buffer.

Notable dependencies:
- External `jasper/jasper.h`.
- Ghostscript non-GC allocator access through `gsmalloc.h`.

Research notes:
- `s_jpxd_buffer_input` has a TODO for allocation failure; if growth allocation fails, the following `memcpy` would use a null buffer.
- The memory stream is opened with `state->bufsize` rather than `state->buffill`, so unused buffer tail bytes may be visible to JasPer.
- As with JBIG2, the implementation intentionally relies on external-library allocation and release cleanup rather than normal GC enumeration.
