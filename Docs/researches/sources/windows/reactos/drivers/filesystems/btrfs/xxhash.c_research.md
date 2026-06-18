# File Research: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.c

## Role

This file embeds Yann Collet's xxHash implementation, adapted for WinBtrfs/ReactOS build environments. It provides one-shot and streaming XXH32/XXH64 hashing plus canonical big-endian serialization helpers. In the Btrfs driver, xxHash is used as a checksum algorithm option where configured by the filesystem.

## Build And Allocation Adaptation

The file includes standard C headers and conditionally includes Windows kernel headers. Allocation is adapted by target:

- Kernel/non-`_USRDLL` builds allocate from `PagedPool` with tag `"XXH "` via `ExAllocatePoolWithTag()` and free with `ExFreePool()`.
- Non-ReactOS user DLL builds use `malloc()` and `free()`.
- ReactOS user DLL builds use `RtlAllocateHeap()` and `RtlFreeHeap()` from the process heap.

It includes `xxhash.h` with `XXH_STATIC_LINKING_ONLY` enabled so internal state structures and canonical helpers are available.

## Tuning And Portability Controls

The file preserves upstream tuning macros:

- `XXH_FORCE_MEMORY_ACCESS`: controls unaligned memory reads through `memcpy`, packed access, or direct casts.
- `XXH_ACCEPT_NULL_INPUT_POINTER`: optional null-input behavior, disabled by default.
- `XXH_FORCE_NATIVE_FORMAT`: optional native-endian mode, disabled by default so hashes are endian-independent.
- `XXH_FORCE_ALIGN_CHECK`: enabled by default on non-x86 architectures and disabled on x86/x64.

It defines compiler inline attributes, rotation helpers, byte-swap helpers, endian detection through `XXH_CPU_LITTLE_ENDIAN`, unaligned/aligned read helpers, and basic fixed-width types when needed.

## XXH32

XXH32 uses 32-bit primes and the standard four-lane accumulator for inputs at least 16 bytes. Core routines include:

- `XXH32_round()`: mixes one 32-bit input word into an accumulator.
- `XXH32_endian_align()`: one-shot hashing over aligned or unaligned input and selected endian mode.
- `XXH32()`: public one-shot API choosing aligned/unaligned and endian mode.
- `XXH32_createState()` / `XXH32_freeState()`: heap state lifecycle.
- `XXH32_reset()`: initializes accumulators from a seed.
- `XXH32_update_endian()` / `XXH32_update()`: streaming update with a 16-byte temporary buffer.
- `XXH32_digest_endian()` / `XXH32_digest()`: finalizes the streaming hash without mutating the state.
- `XXH32_copyState()`: copies streaming state.

Finalization mixes remaining 4-byte and 1-byte tails, then applies avalanche shifts and prime multiplications.

## XXH64

XXH64 mirrors the same structure with 64-bit primes and a 32-byte lane block:

- `XXH64_round()` and `XXH64_mergeRound()` implement accumulator mixing.
- `XXH64_endian_align()` performs one-shot hashing.
- `XXH64()` is the public one-shot API.
- `XXH64_createState()` / `XXH64_freeState()` allocate and free streaming state.
- `XXH64_reset()` initializes state from the seed.
- `XXH64_update_endian()` / `XXH64_update()` process streaming input with a 32-byte temporary buffer.
- `XXH64_digest_endian()` / `XXH64_digest()` finalize from streaming state.
- `XXH64_copyState()` copies state.

Finalization processes 8-byte, 4-byte, and byte tails before applying the XXH64 avalanche.

## Canonical Representation

The file implements canonical conversion helpers:

- `XXH32_canonicalFromHash()`
- `XXH64_canonicalFromHash()`
- `XXH32_hashFromCanonical()`
- `XXH64_hashFromCanonical()`

Canonical form is big-endian, so little-endian hosts byte-swap before writing canonical bytes and use big-endian reads when decoding.

## Dependencies And Integration Points

This file depends on `xxhash.h` for public types, state layouts, version constants, and public API decoration. It is self-contained otherwise, with local wrappers for allocation and memory reads. Driver checksum code can use either one-shot APIs or streaming state APIs depending on how data is buffered.

## Risk Notes

- Null input is not accepted unless `XXH_ACCEPT_NULL_INPUT_POINTER` is defined; default behavior will dereference invalid input.
- Direct or packed memory-access modes are platform/compiler dependent. The default `memcpy` path is the safest.
- Kernel builds allocate streaming state from paged pool, so callers must not use state allocation/free paths at IRQL levels where paged pool access is invalid.
- The code is an embedded third-party implementation; updates should be compared against upstream xxHash behavior and local ReactOS/WinBtrfs allocation changes.
