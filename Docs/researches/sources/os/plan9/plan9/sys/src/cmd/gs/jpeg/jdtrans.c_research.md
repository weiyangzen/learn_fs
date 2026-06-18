# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdtrans.c

Purpose: transcoding decompression support for reading raw DCT coefficient arrays.

Key routines:
- `jpeg_read_coefficients()` reads the whole JPEG image into virtual coefficient-block arrays and returns them.
- `transdecode_master_selection()` initializes only the decompression modules required for coefficient extraction.

Important behavior:
- On first call from `DSTATE_READY`, initializes transcoding mode and enters `DSTATE_RDCOEFS`.
- Consumes input until EOI, returning `NULL` on suspension.
- Sets `buffered_image = TRUE` and always uses a full-image coefficient buffer.
- Selects progressive Huffman or sequential Huffman entropy decoder; arithmetic coding is rejected.
- Initializes progress estimates based on progressive/multiscan/single-scan assumptions.
- After coefficient read completion, state becomes `DSTATE_STOPPING`; coefficient arrays remain available until `jpeg_finish_decompress()`.

Dependencies:
- Input controller, entropy decoder, coefficient controller, memory manager virtual arrays, progress manager.

Notes:
- This is for lossless JPEG transformations/transcoding workflows rather than pixel output.
