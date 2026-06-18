# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imemory.h

Defines interpreter extensions to the Ghostscript allocator interface.

Key points:
- Includes `ivmspace.h` and `gsalloc.h`.
- Declares ref-array allocation, resize, and free APIs.
- Declares string-ref allocation and `gs_register_ref_root`.
- Defines `gs_dual_memory_t`, representing current allocator, system/global/local VM spaces, current space, GC reclaim hook, and store-check masks.
- Notes system VM is immune to even outermost save/restore.
- Notes global VM may equal local in Level 1 configs, but not necessarily in a Level 2 executable running Level 1 mode.
- Warns embedded `gs_dual_memory_t` pointers must not persist across GC.
- Provides structure descriptor macro for `gs_dual_memory_t`.

Research relevance:
- Defines the interpreter’s local/global/system VM abstraction over the base memory manager.
