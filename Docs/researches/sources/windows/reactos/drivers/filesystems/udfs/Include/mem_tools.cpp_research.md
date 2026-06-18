# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.cpp

Optional internal heap manager implementation enabled by `MY_USE_INTERNAL_MEMMANAGER`.

Key responsibilities:
- Provides `DbgTouch()` to force a read from allocated memory.
- Maintains global fixed-size heap frame metadata in `FrameList`, protected by either a spin lock or an `ERESOURCE` wrapper.
- Implements debug dumping and integrity checking for frames and allocation descriptors under `UDF_DBG`.
- Implements best-fit allocation within a frame through `MyAllocatePoolInFrame()`.
- Implements address-to-descriptor/frame lookup through `MyFindMemDescByAddr()` and `MyFindFrameByAddr()`.
- Implements free/coalescing through `MyFreePoolInFrame()` and `MyFreePool()`.
- Implements in-place shrink/grow where possible through `MyResizePoolInFrame()` and fallback allocate/copy/free through `MyReallocPool()`.
- Allocates and frees heap frames with descriptor arrays through `MyAllocInitFrame()` and `MyAllocFreeFrame()`.
- Initializes and releases the allocator through `MyAllocInit()` and `MyAllocRelease()`.
- Provides debug-only base lookup for array/range validation through `MyFindMemBaseByAddr()`.

Important behavior:
- Frames are `MY_HEAP_FRAME_SIZE` bytes, descriptor arrays have `MY_HEAP_MAX_BLOCKS` entries, and descriptors store address plus length/used-bit.
- Allocation is aligned by the macros in `mem_tools.h` before reaching this allocator.
- Freeing clears the used bit, optionally stamps the freed block with `0xDEADDA7A`, checks optional bounds sentinels, and coalesces with adjacent free descriptors.
- Frame descriptors are kept sorted by address, allowing binary-search-like lookup.
- Entire empty frames are returned to the underlying debug allocator.

Dependencies:
- Depends on constants, structures, alignment macros, and tracking flags from `mem_tools.h`.
- Uses `DbgAllocatePool`, `DbgFreePool`, `RtlMoveMemory`, `RtlZeroMemory`, `RtlCopyMemory`, `UDFPrint`, `ASSERT`, and `BrutePoint` from the environment headers.
- Locking maps to kernel-like resource/spin-lock shims from `env_spec_w32.h` or kernel DDK equivalents.

Notable risks:
- The allocator stores addresses in `ULONG`, making it 32-bit-specific.
- `MyReallocPool()` calls `MyAllocatePool()` while already holding the allocator lock; this depends on lock semantics and can deadlock if the lock is not recursively compatible.
- Debug accounting in the grow path adds `len` instead of the growth delta, which appears suspicious.
- Several debug/error paths call `BrutePoint()` and return without fully recovering; this allocator is intended for controlled UDF builds rather than hardened general allocation.
