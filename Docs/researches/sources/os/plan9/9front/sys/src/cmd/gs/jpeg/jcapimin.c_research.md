# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapimin.c

Minimum public API for the JPEG compression object, shared by normal compression and coefficient transcoding.

Key points:
- `jpeg_CreateCompress` validates caller/library version and struct size, preserves the application-provided error manager/client data, zeroes the compressor struct, initializes the memory manager, clears permanent table/module pointers, sets default `input_gamma`, and enters `CSTATE_START`.
- `jpeg_destroy_compress` and `jpeg_abort_compress` are thin wrappers over common `jpeg_destroy`/`jpeg_abort`.
- `jpeg_suppress_tables` toggles every allocated quantization and Huffman table `sent_table` flag, supporting abbreviated datastream workflows.
- `jpeg_finish_compress` completes the active scan/raw/coefficient-writing state, drives remaining multipass output from buffered coefficients, writes EOI, terminates the destination, and aborts the object back to reusable start state.
- `jpeg_write_marker`, `jpeg_write_m_header`, and `jpeg_write_m_byte` allow COM/APP marker emission after compression start and before image data output, with state checks for scan/raw/coefficient modes.
- `jpeg_write_tables` writes a tables-only abbreviated JPEG datastream from `CSTATE_START`, initializes destination and marker writer, emits unsent tables, then deliberately does not abort so application-owned memory pool allocations are not unexpectedly freed.

Dependencies and interactions:
- Depends on `jinclude.h`, `jpeglib.h`, the memory manager, marker writer, destination manager, master controller, and coefficient controller.
- Normal applications also use `jcapistd.c` for `jpeg_start_compress` and scanline/raw write loops; transcoders combine this file with `jctrans.c`.

Risk notes:
- Marker-writing APIs require precise call timing; calling after scanline output begins is rejected.
- `jpeg_finish_compress` cannot tolerate suspension during post-first-pass buffered output and reports `JERR_CANT_SUSPEND`.
- Repeated `jpeg_write_tables` calls may leak image-pool marker/destination workspaces unless the application explicitly calls `jpeg_abort`.
