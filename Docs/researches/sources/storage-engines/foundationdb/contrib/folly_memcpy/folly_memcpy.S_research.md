# sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.S

## Purpose
Folly-derived optimized `memcpy` implementation for x86_64 Linux, using AVX when `__AVX__` is defined and SSE2 otherwise.

## Important APIs, Types, And Functions
Exports global symbol `folly_memcpy` with signature equivalent to `void* folly_memcpy(void* dst, const void* src, uint32_t length)`. Local helper `_memcpy_short` handles lengths 0 through 7 using a nonstandard calling convention.

## Control Flow
`folly_memcpy` saves destination in `%rax` for return, dispatches very short copies to `_memcpy_short`, copies the first and last 8 bytes for small/medium ranges, aligns work into 32-byte groups, then loops over 64-byte chunks using either `movdqu` SSE registers or `vmovdqu` YMM registers. AVX path executes `vzeroupper` before return.

## State And Persistence
No persistent state. It reads and writes caller-provided memory only.

## Dependencies And Integration
Assembled only under `__x86_64__ && __linux__ && !__CYGWIN__`. Intended to be declared by `folly_memcpy.h` under Linux/FreeBSD with AVX.

## Risks
Like standard `memcpy`, overlapping source/destination is undefined. The function accepts a 32-bit length in the public header but uses 64-bit registers, so callers must not pass sizes beyond that contract. Header/CMake/platform guards are not perfectly aligned with the assembly guard. Performance/correctness depends on CPU support matching compile-time AVX selection.

## Test Signals
Byte-for-byte tests for lengths 0 through 128, unaligned source/destination, large buffers, AVX and non-AVX builds, return value identity, and overlap behavior documented as unsupported.
