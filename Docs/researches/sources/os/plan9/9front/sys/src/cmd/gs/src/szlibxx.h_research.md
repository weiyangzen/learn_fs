# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibxx.h

Private implementation definitions for the zlib interface.

Key points:
- Includes `szlibx.h` and zlib’s `zlib.h`.
- Documents why zlib internal allocations must be immovable and GC-traceable.
- Defines `zlib_block_t`, a linked-list node recording each zlib allocation.
- Defines `zlib_dynamic_state_t` with:
  - Ghostscript memory pointer
  - block list
  - embedded `z_stream`
- Provides GC descriptor macros for block and dynamic state structures.
- Declares zlib allocation/free callbacks and dynamic-state allocation/free helpers.

Dependencies and interactions:
- Must be compiled with zlib include path.
- Used only by common/encode/decode zlib filter implementation.

Research relevance:
- Internal memory-safety layer for using zlib inside Ghostscript’s allocator/GC constraints.
