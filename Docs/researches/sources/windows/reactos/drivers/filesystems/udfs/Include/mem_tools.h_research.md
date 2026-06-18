# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.h

Memory allocation abstraction for shared UDF code, selecting either the optional internal frame allocator or system/debug pool wrappers.

Key responsibilities:
- Defines allocation descriptor and frame descriptor structures used by the internal allocator.
- Defines heap constants: used flag, length mask, frame size, maximum frames, maximum blocks, alignment, and page alignment.
- Declares internal allocator APIs when enabled: `MyAllocInit`, `MyAllocRelease`, `MyAllocatePool`, `MyReallocPool`, and `MyFreePool`.
- Defines public macros `MyAllocatePool__`, `MyAllocatePoolTag__`, `MyFreePool__`, `MyReallocPool__`, `MyFreeMemoryAndPointer`, and `MyCheckArray`.
- Supports optional owner tracking, reference/tag tracking, forced nonpaged allocation, internal allocator use, system allocation caller tracking, and simple bounds sentinel checking.
- Provides no-op initialization/release wrappers when the internal allocator is disabled.

Important behavior:
- Allocation sizes are normally rounded by `MyAlignSize__()` to a 64-byte boundary.
- Without the internal allocator, allocations route to `DbgAllocatePoolWithTag()` or `DebugAllocatePool()` and frees route to `DbgFreePool()`.
- With `MY_MEM_BOUNDS_CHECK`, extra bytes are appended and filled with `'A' + i` sentinels, and reallocation/free paths check them.
- `MyReallocPool__()` allocates a new block when aligned sizes differ, copies existing data, zero-fills alignment growth only in the larger-aligned case, and frees the old block.

Dependencies:
- Requires DDK-like pool types/macros and debug allocation wrappers from the UDF environment.
- Internal allocator implementation is in `mem_tools.cpp`.

Notable risks:
- Inline bounds-checking code uses x86 `__asm int 3` in places, so it is compiler/architecture-sensitive.
- Several macros force `NonPagedPool` regardless of the incoming type unless internal allocation mode handles `MyFixMemType()`.
- Because much of the API is macro-based, behavior changes significantly with compile-time flags and can be hard to audit from call sites.
