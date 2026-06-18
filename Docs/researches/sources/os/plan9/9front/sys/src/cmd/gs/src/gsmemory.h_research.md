# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.h

Primary Ghostscript memory allocation API.

Key concepts:
- Distinguishes aligned objects from unaligned strings.
- Supports movable and immovable allocations for GC-aware allocators.
- Defines allocator status, type descriptors, pointer types, GC roots, and the complete `gs_memory_procs_t` interface.
- Raw procedures include immovable byte allocation, resize, free, stable allocator, status, free_all, and consolidate_free.
- Object-level procedures include movable bytes, structs, byte arrays, struct arrays, object size/type, strings, string resize/free, root registration, root unregistration, and enable_free.
- Defines convenience macros such as `gs_alloc_bytes`, `gs_alloc_struct`, `gs_alloc_string`, `gs_free_object`, `gs_memory_status`, and `gs_consolidate_free`.
- Defines `FREE_ALL_DATA`, `FREE_ALL_STRUCTURES`, `FREE_ALL_ALLOCATOR`, and `FREE_ALL_EVERYTHING`.
- Declares const-free helpers, bytestring free helpers, struct-array resize helper, root helper, no-op free/consolidate procedures, and raw immutable struct allocation.
- Defines `gs_memory_common`, including stable allocator, procedure table, library context, optional PCL/PXL memory head, and non-GC parent allocator.
- Defines concrete `struct gs_memory_s`.

Research notes:
- This is a foundational API; most allocator implementations in this group are concrete wrappers around this contract.
- Comments explicitly warn that allocator alignment is not guaranteed beyond hardware requirements.
