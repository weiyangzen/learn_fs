# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjpegc.c

Implements common IJG libjpeg wrapper behavior for encoding and decoding.

Key points:
- Provides prototypes for non-public IJG memory-manager functions when `jmemsys.h` is unavailable.
- `gs_jpeg_error_setup` installs Ghostscript-specific `error_exit` and `emit_message` handlers over IJG's standard error manager.
- Fatal IJG errors are converted to `longjmp` back into wrapper functions.
- `gs_jpeg_log_error` formats the IJG error message and reports it through the stream state's `report_error` callback.
- Table allocation and destroy wrappers isolate `setjmp` side effects.
- Replaces IJG small/large allocation hooks with Ghostscript memory allocations and tracks allocated blocks in `jpeg_block_t` linked lists for freeing.
- Disables backing-store use by raising IJG `JERR_NO_BACKING_STORE`.

Dependencies and interactions:
- Uses `sdct.h` JPEG stream data structures and `sjpeg.h` declarations.

Research relevance:
- This file is the core safety/ownership adapter around libjpeg's error and memory systems.
