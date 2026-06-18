# sources/storage-engines/sqlite/src/hwtime.h

## Purpose

`hwtime.h` provides an inline `sqlite3Hwtime()` routine for high-resolution timing in profiling, debugging, and analysis builds. It is not intended for normal deliverables; unsupported platforms fall back to a zero-returning function.

## Important APIs, Types, And Functions

The only API is `sqlite3Hwtime()`, returning a `sqlite_uint64` or `sqlite3_uint64` counter value depending on branch typedef usage. Implementations are selected for MSVC/Win32 via `QueryPerformanceCounter()`, GCC x86/i586 and x86_64 via `rdtsc`, GCC aarch64 via `mrs cntvct_el0`, GCC ppc via a stable time-base read loop, and a fallback stub returning zero.

## Control Flow

Preprocessor checks choose exactly one inline implementation. The x86 variants read low/high TSC registers and combine them. The aarch64 branch reads the virtual counter register. The ppc branch reads upper/lower/upper time-base values until the upper value is stable. The fallback has no timing side effect.

## State And Persistence Behavior

There is no mutable SQLite state and no persistence. Return values are raw platform counters, not normalized wall-clock time. Their units, monotonicity, synchronization across cores, and availability depend on platform and privilege behavior.

## Dependencies And Integration Points

The header depends on platform compiler macros and, on Windows, `windows.h` plus `profileapi.h`. It is referenced by profiling/debug code such as `VDBE_PROFILE` paths, with `global.c` offering `sqlite3NProfileCnt` as an alternate counter in some profiling builds.

## Risks

Inline assembly and platform macros are the main portability risks. `rdtsc` can be non-serializing and may not represent elapsed real time across frequency changes or CPU migration on older systems. Aarch64 access to `cntvct_el0` depends on OS configuration. The fallback silently returns zero, so profiling consumers must tolerate no timing support. Typedef spelling differences (`sqlite_uint64` vs `sqlite3_uint64`) must match surrounding SQLite headers.

## Test Signals

Signals include compilation on each supported architecture/compiler branch, smoke tests that repeated calls are callable and generally nondecreasing where the platform promises it, and profiling builds verifying zero fallback does not break VDBE profile output. Cross-compilation is useful because most risk is preprocessor/assembler compatibility rather than algorithmic behavior.
