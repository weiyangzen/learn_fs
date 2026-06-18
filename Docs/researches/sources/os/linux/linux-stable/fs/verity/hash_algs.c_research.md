# File Research: sources/os/linux/linux-stable/fs/verity/hash_algs.c

Defines fs-verity supported hash algorithms and hashing helpers. The table currently supports SHA-256 and SHA-512, mapping fs-verity UAPI algorithm numbers to crypto/hash algorithm ids, digest sizes, and compression block sizes.

`fsverity_get_hash_alg()` validates an algorithm number and logs unknown values. `fsverity_prepare_hash_state()` precomputes salted initial hash state by zero-padding the salt to the hash compression block size, allowing salted block hashing to run as efficiently as unsalted hashing. `fsverity_hash_block()` hashes one Merkle block using either the precomputed salted state or direct buffer hashing. `fsverity_hash_buffer()` hashes arbitrary descriptor/buffer data.

`fsverity_check_hash_algs()` sanity-checks the table at init: algorithm 0 must remain unused, digest sizes must fit fs-verity limits, digest and block sizes must be powers of two, and `HASH_ALGO_*` metadata must match.
