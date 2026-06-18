# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapimin.c

Minimum decompression API needed for full decompression and transcoding.

Key behavior:
- `jpeg_CreateDecompress` validates ABI version/struct size, preserves application error/client fields, zeros the decompressor struct, initializes memory management, marker reader, input controller, and start state.
- Provides destroy/abort wrappers over common API routines.
- Guesses JPEG input colorspace and default output colorspace from component count, JFIF marker, Adobe marker, Adobe transform, and component IDs.
- Initializes decompression defaults: scaling, gamma, buffered/raw modes, DCT method, fancy upsampling, block smoothing, and color quantization options.
- `jpeg_read_header` drives input consumption until SOS or EOI and returns header status codes.
- `jpeg_consume_input` is the central decompressor input state machine.
- Provides helpers for input completion, multiple-scan detection, and final decompression cleanup.

Dependencies:
- Uses decompressor memory manager, marker reader, input controller, source manager, master controller, and common abort/destroy routines.

Notable risks:
- Color-space inference is heuristic because JPEG lacks a complete standard colorspace declaration.
- Empty input is fatal in the stdio source manager; truncated nonempty input may be converted to a fake EOI.
- `jpeg_finish_decompress` errors if the caller has not consumed all output scanlines in non-buffered mode.
