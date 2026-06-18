# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/memory.c

## Role

`memory.c` provides libFLAC allocation helpers for aligned arrays and one local safe multiplication allocator. It centralizes the pattern where callers keep both the original malloc pointer for `free()` and an aligned alias for SIMD-friendly access.

## Major Functions

- `FLAC__memory_alloc_aligned()` allocates raw memory and returns both the base allocation and an aligned address through an out parameter.
- `FLAC__memory_alloc_aligned_int32_array()`
- `FLAC__memory_alloc_aligned_uint32_array()`
- `FLAC__memory_alloc_aligned_int64_array()`
- `FLAC__memory_alloc_aligned_uint64_array()`
- `FLAC__memory_alloc_aligned_unsigned_array()`
- `FLAC__memory_alloc_aligned_real_array()` when not building `FLAC__INTEGER_ONLY_LIBRARY`
- `safe_malloc_mul_2op_p()` allocates `size1 * size2` with overflow checking and converts zero-size requests into `malloc(1)`.

## Important Implementation Details

If `FLAC__ALIGN_MALLOC_DATA` is defined, `FLAC__memory_alloc_aligned()` overallocates by 31 bytes and rounds the returned alias up to a 32-byte boundary. Otherwise, the aligned pointer is simply the base pointer.

Each typed array allocator checks `elements > SIZE_MAX / sizeof(*pu)` before multiplying. It allocates a new buffer first, then frees the previous `*unaligned_pointer` only after the new allocation succeeds. This avoids losing the old allocation on failure.

The functions use small unions to store `void *` and typed pointers, avoiding C99 strict-aliasing problems when receiving the aligned address through a `void **`.

## Risks / Edge Cases

- The API requires `unaligned_pointer` and `aligned_pointer` to be distinct, non-null output locations. These are asserted, not handled in release builds.
- `elements > 0` is asserted. Zero-length array allocation is not a supported caller contract for the typed aligned array helpers.
- Callers must free the unaligned/base pointer, not the aligned alias.
- `safe_malloc_mul_2op_p()` differs from direct `malloc(0)` by always allocating at least one byte when either operand is zero, following the local FLAC convention.

## Dependencies

Uses `private/memory.h`, `FLAC/assert.h`, `share/compat.h`, and `share/alloc.h`. It depends on libFLAC typedefs for fixed-width integer and real sample types.
