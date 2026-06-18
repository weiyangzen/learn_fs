<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha1.c -->
# sources/user-network-fs/libsmb2/lib/sha1.c

## Purpose

`sha1.c` implements SHA-1 from RFC 4634 when `USE_SHA1` is enabled. It provides reset, input, final partial-bit, and result APIs over `SHA1Context`.

## Important APIs, Types, And Functions

Public functions are `SHA1Reset`, `SHA1Input`, `SHA1FinalBits`, and `SHA1Result`. Internal helpers are `SHA1Finalize`, `SHA1PadMessage`, and `SHA1ProcessMessageBlock`. Macros include `SHA1_ROTL` and `SHA1AddLength`.

## Control Flow

`SHA1Reset` seeds the five initial hash words and clears counters. `SHA1Input` appends bytes to a 64-byte block, increments the 64-bit bit count, and processes a block when full. `SHA1FinalBits` validates a 1-to-7-bit suffix, updates length, and finalizes with the proper marker bit. `SHA1Result` finalizes if needed and writes big-endian digest bytes. The compression function expands 16 input words to 80 and runs the four SHA-1 rounds.

## State And Persistence Behavior

All state is caller-owned in `SHA1Context`. Finalization clears the pending message block and length counters and marks `Computed`. `Corrupted` records overflow, null/state errors, or previous failure. No state is persisted.

## Dependencies And Integration Points

It depends on `compat.h`, `sha.h`, and `sha-private.h`. Because `USE_SHA1` defaults to 0 in `sha.h`, this file may compile to no public functions unless enabled by the build.

## Risks And Edge Cases

SHA-1 is cryptographically weak for collision resistance and should not be used for new integrity designs. The byte-at-a-time input loop is simple but slow for large buffers. The length overflow path sets `Corrupted` to integer `1`, not the named `shaInputTooLong`, matching this RFC code but less expressive.

## Test Signals

Use FIPS SHA-1 known-answer vectors, million-`a` input, incremental byte and multi-byte updates, final-bit vectors, length overflow simulation, null input handling, and state-error checks after result/final-bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha1.c -->
