# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegc.c

Common JPEG wrapper implementation for IJG encode/decode integration and memory management.

Key behavior:
- Installs Ghostscript error handlers over IJG’s `jpeg_error_mgr`.
- `gs_jpeg_error_exit` converts IJG fatal errors to `longjmp` through the enclosing stream data.
- `gs_jpeg_emit_message` ignores warnings unless `Picky` is set, in which case warnings become errors.
- `gs_jpeg_log_error` formats IJG error text through the stream’s `report_error` callback.
- Wrapper functions around quant/huffman table allocation and `jpeg_destroy` isolate `setjmp`.
- Overrides IJG memory-manager entry points (`jpeg_get_small`, `jpeg_get_large`, frees, availability, backing store) to allocate through Ghostscript memory and track blocks.

Notable dependencies:
- IJG headers via `jpeglib_.h`, `jerror_.h`.
- DCT stream state from `sdct.h`.
- Optional `jmemsys.h` prototypes controlled by `gconfig_.h`.

Research notes:
- Uses a private linked list of `jpeg_block_t` records to track allocations for cleanup/debugging.
- Backing store is deliberately unsupported and raises IJG `JERR_NO_BACKING_STORE`.
