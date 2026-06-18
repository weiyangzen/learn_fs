# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imemory.h

Defines interpreter extensions to the Ghostscript allocator interface.

Key points:
- Includes `ivmspace.h` and `gsalloc.h`.
- Declares ref-array allocation APIs:
  - `gs_alloc_ref_array`
  - `gs_resize_ref_array`
  - `gs_free_ref_array`
- Declares string-ref allocation:
  - `gs_alloc_string_ref`
- Declares `gs_register_ref_root`.
- Defines `gs_dual_memory_t`, representing interpreter VM allocation state:
  - current allocator
  - system/global/local `vm_spaces`
  - current space
  - GC reclaim hook
  - store-check masks
- Notes:
  - system VM is immune to even outermost save/restore.
  - in Level 1 configs global may equal local, but not necessarily in a Level 2 executable running Level 1 mode.
  - embedded `gs_dual_memory_t` pointers must not persist across GC.
- Provides structure descriptor macro for `gs_dual_memory_t`.

Dependencies and interactions:
- Used by interpreter allocation, save/restore, GC, stacks, names, and dictionaries.

Research relevance:
- Defines the interpreter’s local/global/system VM abstraction over the base memory manager.
