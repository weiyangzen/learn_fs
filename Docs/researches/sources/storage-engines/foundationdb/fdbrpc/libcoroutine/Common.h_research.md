# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.h

## Purpose

`Common.h` is the portability and allocator facade for `libcoroutine`. It normalizes integer typedefs on older systems, handles Windows and DBCS feature macros, exposes `BASEKIT_API`, and maps `io_*` allocation functions either to debug wrappers or libc.

## Important APIs, types, and functions

The file defines fallback `uint8_t`, `int8_t`, `uint16_t`, `int16_t`, `uint32_t`, `int32_t`, `uint64_t`, and `int64_t` for platforms without standard integer headers. It sets Windows-specific macros such as `HAS_FIBERS` and `ON_WINDOWS`, DBCS helpers `ismbchar()` and `mbcharlen()`, allocator macros `io_malloc`, `io_calloc`, `io_realloc`, `io_free`, and declarations for `cpalloc()`, `io_freerealloc()`, `io_isBigEndian()`, and `io_uint32InBigEndian()`.

## Control flow, state, and persistence

There is no direct runtime flow. Compile-time branches decide whether coroutine code uses Win32 fibers, system headers, debug allocation tracking, or direct libc allocation. The optional allocation state lives in `Common.c`; otherwise there is no state.

## Dependencies and integration points

`Coro.c` and `Common.c` include this header. On Windows it includes `winsock2.h`, `memory.h`, `string.h`, and `malloc.h`, and maps `usleep()` to `Sleep()`. It affects `Coro.h` implementation choice indirectly by defining `HAS_FIBERS`.

## Risks and test signals

The header carries many legacy platform branches and globally visible macro rewrites, so include-order changes can cause surprises. In tracking mode, macro replacement changes allocation semantics and exposes the nonzeroing `io_real_calloc()` issue in `Common.c`. Test by compiling both Windows/fiber and POSIX/ucontext builds and by running coroutine lifecycle tests under normal and allocation-checking configurations.
