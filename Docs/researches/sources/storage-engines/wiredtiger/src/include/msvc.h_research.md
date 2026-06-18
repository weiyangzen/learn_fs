# sources/storage-engines/wiredtiger/src/include/msvc.h

## Purpose
Provides the MSVC/x64 compiler and atomic abstraction layer for WiredTiger, including barriers, pause instructions, packing attributes, printf-format attribute no-ops, atomic load/store/add/sub/CAS helpers, and Windows-compatible type behavior.

## Important APIs, Types, And Functions
- Requires `_M_AMD64`; defines `inline` for C and maps `__PRETTY_FUNCTION__` to `__FUNCSIG__`.
- Defines MSVC format strings `WT_PTRDIFFT_FMT` and `WT_SIZET_FMT`.
- `WT_PACKED_STRUCT_BEGIN` and `WT_PACKED_STRUCT_END` implement packed structure declarations with `__pragma(pack)`.
- `WT_COMPILER_BARRIER`, `WT_FULL_BARRIER`, `WT_PAUSE`, `WT_ACQUIRE_BARRIER`, and `WT_RELEASE_BARRIER` wrap MSVC intrinsics.
- `WT_ATOMIC_FUNC_STORE_LOAD`, `WT_ATOMIC_CAS_FUNC`, and `WT_ATOMIC_FUNC` generate typed atomic APIs for integer, bool, size, and uintmax types.
- Pointer and generic relaxed load/store macros, enum atomics, and double relaxed accessors fill out platform compatibility.

## Control Flow
Atomic generator macros emit families of static inline functions. Read/write relaxed helpers are plain loads/stores on x86/x64 for historical/performance reasons. Add/sub and CAS use `_Interlocked*` intrinsics. Acquire/release wrappers issue compiler barriers because x86 TSO provides the needed hardware ordering for these cases.

## State And Persistence Behavior
This header does not own persistent state, but it defines how shared in-memory state is synchronized on Windows builds. Its behavior affects correctness for locks, flags, reference states, statistics, and vtable wrappers throughout WiredTiger.

## Dependencies And Integration Points
Depends on `<intrin.h>` and Windows/MSVC intrinsic signatures. It must match the GCC/Clang atomic API names used by shared WiredTiger code. Integrated with mutexes, sessions, file handles, ref state, load control, statistics, and all `wt_shared` fields.

## Risks
Relaxed helpers are not true C11 atomics and rely on x86 memory model and WiredTiger's historical assumptions. Casts to interlocked intrinsic pointer types must match size/alignment. The header only supports x64 MSVC; accidental ARM or 32-bit builds fail intentionally. Differences from GCC atomics can hide or expose races differently across platforms.

## Test Signals
Windows CI should compile every generated atomic family, exercise locks and ref-state CAS, run TSan-equivalent/static race checks where possible, validate packed structure layout, and stress concurrent flag/stat updates under MSVC.
