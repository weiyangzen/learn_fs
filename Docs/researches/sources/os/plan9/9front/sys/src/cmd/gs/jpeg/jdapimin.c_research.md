# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapimin.c

Minimum public API for JPEG decompression and transcoding header consumption.

Key points:
- `jpeg_CreateDecompress` validates version/struct size, preserves error manager/client data, zeroes the decompressor struct, initializes memory manager, clears table pointers, initializes marker reader and input controller, and enters `DSTATE_START`.
- Destroy/abort wrappers delegate to common routines.
- `default_decompress_parms` guesses JPEG and output colorspaces from component count, JFIF/Adobe markers, transform code, and component IDs; then sets scale, gamma, buffering, raw output, DCT, upsampling, block smoothing, and color quantization defaults.
- `jpeg_read_header` drives input consumption to SOS or EOI, maps return codes to public header results, supports tables-only streams, and handles suspension.
- `jpeg_consume_input` is the decompressor input state machine, initializing source/input controller at start, consuming headers, installing defaults on SOS, and delegating later states to the input controller.
- `jpeg_input_complete` and `jpeg_has_multiple_scans` expose input-controller state.
- `jpeg_finish_decompress` verifies final output completion, finishes the output pass, consumes input to EOI, terminates the source, and aborts back to reusable start state.

Dependencies and interactions:
- Depends on decompressor marker reader/input controller/master modules outside this group.
- Shared cleanup is in `jcomapi.c`; standard scanline APIs are in `jdapistd.c`.

Risk notes:
- Colorspace detection is heuristic because JPEG streams often lack definitive colorspace metadata.
- `jpeg_finish_decompress` requires all output scanlines/raw rows to be consumed unless buffered-image mode is active.
- Suspension-aware callers must inspect `FALSE`/`JPEG_SUSPENDED` returns and retry.
