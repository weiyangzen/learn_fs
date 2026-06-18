# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibc.c

Purpose: shared zlib stream support for Ghostscript compression and decompression filters.

Key contents:
- Defines GC descriptors for zlib block tracking, dynamic state, and public zlib stream state.
- Implements `s_zlib_set_defaults`.
- Implements `s_zlib_alloc_dynamic_state` to allocate immovable `zlib_dynamic_state_t`, configure `zalloc`, `zfree`, and `opaque`.
- Implements `s_zlib_free_dynamic_state`.
- Implements zlib-compatible `s_zlib_alloc` and `s_zlib_free`, tracking every zlib allocation in a linked list of `zlib_block_t`.

Dependencies: Ghostscript memory/structure headers, `strimpl.h`, `szlibxx.h`, `zconf.h`.

Integration notes: bridges zlib’s allocator callbacks into Ghostscript’s stable/immovable allocation model so GC can track allocations.

Risks: freeing unrecorded data is logged rather than fatal; allocation tracking correctness is essential because zlib private memory is external to normal movable stream state.
