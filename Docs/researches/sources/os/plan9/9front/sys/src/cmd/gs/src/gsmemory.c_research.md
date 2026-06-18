# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.c

Generic allocator support shared by Ghostscript memory implementations.

Key behavior:
- Defines allocator debug fill bytes and structure descriptors for free blocks, byte blocks, GC roots, and const strings.
- Implements bytestring and const-bytestring GC enumerate/relocate procedures, preserving substring offset when backing bytes object moves.
- `gs_alloc_memset` fills arbitrarily large regions in `max_int` chunks.
- `gs_resize_struct_array` allocates or resizes typed struct arrays and checks type in DEBUG builds.
- `gs_raw_alloc_struct_immovable` aliases raw struct allocation to immutable byte allocation sized from the type descriptor.
- Provides no-op free and consolidate functions used when freeing is disabled.
- Provides const-pointer freeing helpers by deconstifying before dispatch.
- Frees `gs_bytestring`/`gs_const_bytestring` through object or string paths depending on representation.
- Exposes type descriptor size/name accessors.
- `gs_register_struct_root` wraps `gs_register_root` with `ptr_struct_type`.
- DEBUG reference-count tracing prints type names and refcount transitions.
- `rc_free_struct_only` frees a reference-counted object through its memory.
- `basic_enum_ptrs` and `basic_reloc_ptrs` implement generic descriptor-driven GC traversal and relocation, including supertype traversal.

Dependencies:
- Uses `gsmemory.h`, `gsmdebug.h`, `gsrefct.h`, and `gsstruct.h`.

Research notes:
- This file is infrastructure for both GC and non-GC allocators.
- The descriptor-driven pointer traversal is the main generic GC support in this file.
