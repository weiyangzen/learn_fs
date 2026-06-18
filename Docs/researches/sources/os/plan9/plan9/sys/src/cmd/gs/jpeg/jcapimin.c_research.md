# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapimin.c

Minimum public API implementation for the compression side of the IJG JPEG library, used by both full compression and transcoding-only cases.

Key behavior:
- `jpeg_CreateCompress` validates library version and struct size, preserves caller-provided error manager and client data, zeroes the compression object, initializes the memory manager, clears permanent object pointers/tables, sets default input gamma, and enters `CSTATE_START`.
- `jpeg_destroy_compress` and `jpeg_abort_compress` delegate to common destroy/abort routines.
- `jpeg_suppress_tables` marks all defined quantization and Huffman tables as already-written or not-written for abbreviated stream control.
- `jpeg_finish_compress` validates state, finishes the first pass if scanline/raw input was active, runs remaining multipass coefficient-output passes, writes the file trailer, terminates destination output, and aborts/reset-frees working memory.
- `jpeg_write_marker` writes a complete COM/APPn-style marker between start-compress and first data write.
- `jpeg_write_m_header` and `jpeg_write_m_byte` provide piecemeal marker writing.
- `jpeg_write_tables` emits an abbreviated table-only datastream, initializing the destination and marker writer, writing tables, terminating the destination, and intentionally not aborting afterward to avoid freeing application-owned allocations from the JPEG memory manager.

Dependencies:
- Internal IJG headers `jinclude.h` and `jpeglib.h`.
- Calls memory manager, marker writer, destination manager, master controller, coefficient controller, and common API routines.

Research notes:
- State checks are strict and protect public API call ordering.
- Marker writing is only legal before the first scanline/raw-data write.
- The table-writing behavior intentionally changed from older releases to avoid surprising applications, at the cost of possible leaks if callers repeat it without resetting.
