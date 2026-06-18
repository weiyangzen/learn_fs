# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idosave.h

Declares support functions for save/restore change recording:
- `alloc_save_change`
- `alloc_save_change_in`

The comment explains why the containing object ref is required: the allocator must choose the correct VM save chain and must know whether the container is a ref array/dictionary or struct for GC tracing and relocation.
