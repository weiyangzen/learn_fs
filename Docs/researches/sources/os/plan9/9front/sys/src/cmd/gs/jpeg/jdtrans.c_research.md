# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdtrans.c

Transcoding decompression path for reading raw DCT coefficient arrays.

Key points:
- `jpeg_read_coefficients` initializes a reduced decompressor pipeline when called from `DSTATE_READY`, then consumes input until EOI into full-image coefficient arrays.
- Returns `NULL` on input suspension and otherwise returns the coefficient virtual-array descriptors.
- Can also expose coefficient arrays during buffered-image decompression after an output pass.
- Sets standalone coefficient-read state to `DSTATE_STOPPING` so `jpeg_finish_decompress` performs cleanup correctly.
- `transdecode_master_selection` marks `buffered_image`, selects progressive or sequential Huffman entropy decoding, always initializes full coefficient buffering, realizes virtual arrays, and starts the first input pass.
- Initializes progress estimates for progressive, multiscan, and single-scan inputs.

Dependencies and interactions:
- Requires `jpeg_read_header` from `jdapimin.c` before use.
- Bypasses normal `jdmaster.c` output modules and uses `jdinput.c`, entropy decoders, and `jdcoefct.c`.
- Coefficient arrays can be handed to compressor-side `jpeg_write_coefficients`.

Risk notes:
- Arithmetic-coded JPEG is not implemented.
- Progressive coefficient reads require `D_PROGRESSIVE_SUPPORTED`.
- Any later library call may reposition virtual-array backing storage, so callers cannot keep raw access pointers across calls.
