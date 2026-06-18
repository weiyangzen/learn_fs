# File Research: sources/windows/winbtrfs/src/blake2b-ref.c

## Purpose

`blake2b-ref.c` is a compact reference implementation of unkeyed BLAKE2b hashing. In WinBtrfs it supplies the hash primitive used when the filesystem checksum type is BLAKE2.

## Main Constants

- `blake2b_IV[8]`
  - Standard BLAKE2b initialization vector.
- `blake2b_sigma[12][16]`
  - Standard message word permutation schedule for 12 compression rounds.

## Main Routines

- `blake2b_init0()`
  - Clears the state and initializes `h[]` from the IV.
- `blake2b_init_param()`
  - XORs the BLAKE2b parameter block into the IV-derived state.
  - Stores the requested digest length.
- `blake2b_init()`
  - Builds a default unkeyed parameter block:
    - digest length from caller
    - fanout 1
    - depth 1
    - zero salt/personalization/reserved fields
- `blake2b_increment_counter()`
  - Adds processed bytes to the 128-bit byte counter.
- `blake2b_set_lastnode()`, `blake2b_is_lastblock()`, `blake2b_set_lastblock()`
  - Manage final-block flags.
- `blake2b_compress()`
  - Loads 16 little-endian message words.
  - Initializes the 16-word working vector from state, IV, counters, and finalization flags.
  - Runs 12 `ROUND()` invocations using the BLAKE2b `G()` mixing function.
  - Folds the working vector back into `S->h`.
- `blake2b_update()`
  - Buffers partial input.
  - Compresses full 128-byte blocks.
  - Leaves the last block uncompressed until finalization.
- `blake2b_final()`
  - Validates output buffer and state.
  - Increments counter by remaining buffered bytes.
  - Marks the final block.
  - Pads the buffer with zeros, compresses, stores the 64-byte digest to a temporary buffer, and copies the requested digest length.
- `blake2b()`
  - Public wrapper: initialize, update once, finalize.

## Behavior

The exposed `blake2b()` interface supports one-shot unkeyed hashing with caller-selected output length. It does not expose keyed hashing, streaming state, salt, personalization, tree hashing, or XOF behavior to callers.

## Notable Details

- `blake2b_final()` returns an error for null output or too-small output, but `blake2b()` ignores return values from `update()` and `final()`.
- `blake2b_init()` casts `outlen` to `uint8_t` without explicit range validation. Normal Btrfs use should request a valid digest length.
- The implementation includes `<stdio.h>` but does not use it.
- Input length is `size_t`; a comment notes that `inlen` ideally should be `uint64_t`.
- The code is reference-oriented rather than platform-optimized.

## Integration

The implementation depends on `blake2-impl.h` for endian helpers, state/parameter definitions, constants, and rotate operations. Driver checksum code can call `blake2b(out, outlen, in, inlen)` as a simple one-shot digest primitive.
