# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibxx.h

Purpose: private zlib implementation definitions.

Key contents:
- Includes `szlibx.h` and `zlib.h`.
- Defines `zlib_block_t` linked-list nodes for GC-visible zlib allocation tracking.
- Defines `zlib_dynamic_state_t` with Ghostscript memory pointer, allocation list, and `z_stream`.
- Declares private structure descriptor macros for block and dynamic state.
- Declares allocator/free callbacks and dynamic-state allocation/free helpers.

Dependencies: zlib headers and Ghostscript memory descriptor macros.

Integration notes: shared by `szlibc.c`, `szlibd.c`, and `szlibe.c`.

Risks: header requires compile include path for zlib source/include directory.
