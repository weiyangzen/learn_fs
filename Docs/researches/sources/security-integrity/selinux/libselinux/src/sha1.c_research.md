<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.c -->
# sources/security-integrity/selinux/libselinux/src/sha1.c

## Purpose
Implements SHA-1 hashing for libselinux digest features, especially file-context digest generation.

## Important APIs, Types, And Functions
`Sha1Initialise()`, `Sha1Update()`, and `Sha1Finalise()` operate on `Sha1Context` and produce `SHA1_HASH`. `TransformFunction()` is the internal 80-round compression function.

## Control Flow
Update accumulates bit counts, fills 64-byte blocks, and processes full blocks. Finalise appends SHA-1 padding, appends the big-endian length, and extracts the digest bytes.

## State And Persistence Behavior
State is caller-owned hash context memory. No external state is changed.

## Dependencies And Integration Points
Used by label digest code. Uses `ignore_unsigned_overflow_` because SHA-1 arithmetic intentionally wraps.

## Risks And Test Signals
Risks include integer-size limits (`uint32_t BufferSize`), endian/block handling, and cryptographic obsolescence if used for security instead of change detection. Tests should include standard SHA-1 vectors, incremental updates, empty input, boundary sizes around 64 bytes, and large multi-block inputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.c -->
