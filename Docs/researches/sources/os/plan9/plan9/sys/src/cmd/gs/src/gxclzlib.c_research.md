# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclzlib.c

## Purpose
Initializes zlib compressor/decompressor prototype states for RAM-based command-list band lists.

## Public Surface
- `gs_cl_zlib_init(gs_memory_t *mem)`: initializes global zlib encode/decode stream states with raw deflate mode.
- `clist_compressor_state(void *client_data)`: returns the compressor prototype.
- `clist_decompressor_state(void *client_data)`: returns the decompressor prototype.

## Implementation
- Stores two static `stream_zlib_state` objects.
- Sets zlib defaults, sets `no_wrapper = true`, and assigns encode/decode templates.
- The `mem` and `client_data` arguments are not used by the current implementation.

## Dependencies
Requires Ghostscript zlib stream support via `szlibx.h` and clist memory interfaces.

## Risks and Notes
- Static state means callers receive prototypes to copy or reference; mutation after initialization would be global.
- The file must be compiled with zlib include paths, as noted by the source comment.

Filesystem relevance: none directly. It configures compression for in-memory band-list data.
