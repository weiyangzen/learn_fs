# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/memory.h

## Role

`private/memory.h` declares libFLAC memory allocation helpers, especially aligned array allocation for SIMD-friendly buffers.

## API Surface

It declares generic `FLAC__memory_alloc_aligned()` plus typed aligned array allocators for signed/unsigned 32-bit and 64-bit integers, unsigned integers, and `FLAC__real` when floating-point analysis is enabled. It also declares `safe_malloc_mul_2op_p()`.

## Important Contracts

Aligned allocation returns both the original unaligned pointer and an aligned pointer. The original pointer must be used for `free()`. Typed array helpers replace caller-managed old buffers only after successful allocation in the implementation.

## Risks / Edge Cases

- Callers must keep unaligned and aligned pointer variables distinct.
- Zero-element allocation is not the intended typed-array contract in the implementation.
- `safe_malloc_mul_2op_p()` differs from raw `malloc()` by guarding multiplication overflow and avoiding zero-byte allocation.

## Dependencies

Includes `private/float.h` and `FLAC/ordinals.h`.
