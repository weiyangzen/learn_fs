# File Research: sources/os/linux/linux/fs/verity/hash_algs.c

## Purpose
Defines and implements fs-verity hash algorithm support for SHA-256 and SHA-512.

## Main Functions
- `fsverity_get_hash_alg()`: validates and returns hash algorithm metadata by fs-verity algorithm number.
- `fsverity_prepare_hash_state()`: precomputes salted initial SHA state after zero-padding salt to the hash compression block size.
- `fsverity_hash_block()`: hashes one Merkle block, using precomputed salted state if present.
- `fsverity_hash_buffer()`: hashes arbitrary buffer data with SHA-256 or SHA-512.
- `fsverity_check_hash_algs()`: init-time sanity checks algorithm numbering, digest limits, power-of-two assumptions, and `HASH_ALGO_*` mappings.

## Important Design Points
- Algorithm index 0 must remain unallocated/reserved.
- Salt is padded to the hash compression block size to avoid buffered internal hash state and keep salted hashing efficient.
- Implementation assumes digest and hash block sizes are powers of two.
- Uses crypto library SHA routines directly rather than the asynchronous crypto API.

## Cross-File Relationships
- Used by Merkle tree construction, verification, descriptor digest computation, and measurement.
- Relies on `hash_digest_size[]` mapping from kernel hash info.

## Risks / Review Notes
- Adding a new algorithm requires preserving numbering semantics and updating sanity constraints.
- The salt precompute path allocates memory and must be freed via tree params cleanup.
