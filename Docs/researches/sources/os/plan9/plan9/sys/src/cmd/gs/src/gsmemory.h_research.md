# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.h

Primary Ghostscript memory-manager interface. It defines opaque structure descriptors, allocator type, pointer type, GC root type, memory status reporting, raw allocator procedures, object/string allocation procedures, root registration, free enabling, stable allocator access, consolidation, and `free_all` flags.

The API distinguishes objects from strings: objects are aligned and cannot have interior references, while strings may be unaligned and may be referenced internally. It also supports movable versus immovable allocations for GC-capable allocators.

`gs_memory_common` embeds stable allocator, procedure table, library context, a PCL/PXL memory tracking head, and non-GC parent allocator pointer. The header provides the macros used throughout the Ghostscript codebase for allocation, resize, free, type/size lookup, and root management.
