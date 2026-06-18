# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibc.c

Common code for zlib encode/decode stream filters.

Key behavior:
- Defines structure descriptors for zlib block tracking, dynamic state, and public zlib stream state.
- `s_zlib_set_defaults` sets zlib parameters:
  - `windowBits = MAX_WBITS`
  - wrapper enabled
  - default compression level/method/strategy
  - `memLevel = min(MAX_MEM_LEVEL, 8)`
  - clears dynamic pointer
- `s_zlib_alloc_dynamic_state` allocates immovable zlib dynamic state, installs `s_zlib_alloc`/`s_zlib_free` callbacks into `z_stream`, and links the Ghostscript allocator.
- `s_zlib_free_dynamic_state` frees the dynamic state object.
- `s_zlib_alloc` allocates zlib data from `stable_memory`, records each block in a doubly linked list, and returns zlib-compatible pointers.
- `s_zlib_free` frees data, finds/removes the recorded block, and logs if zlib frees unrecorded data.

Dependencies and interactions:
- Includes Ghostscript memory/GC headers, `strimpl.h`, `szlibxx.h`, and `zconf.h`.
- Shared by `szlibd.c` and `szlibe.c`.

Research relevance:
- Bridges zlib’s allocator model into Ghostscript’s movable/GC-aware memory world by keeping immovable and traceable allocations.
