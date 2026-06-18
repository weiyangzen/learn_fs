# sources/security-integrity/fsverity-utils/lib/compute_digest.c

Purpose: This file implements `libfsverity_compute_digest()`, including Merkle tree construction, fs-verity descriptor generation, metadata callback reporting, and final file digest hashing.

Important APIs and functions: Internal helpers include `hash_one_block`, `block_is_full`, `report_merkle_tree_size`, `report_merkle_tree_block`, `report_descriptor`, and `compute_root_hash`. The exported function validates `libfsverity_merkle_tree_params`, selects the hash algorithm, constructs `struct fsverity_descriptor`, computes the root hash, and returns `struct libfsverity_digest`.

Control flow and state: Data is read incrementally through caller-supplied `read_fn`. Pending data/tree blocks are buffered per level, salted and zero-padded before hashing, and optional callbacks receive tree size, tree blocks, and descriptor. Empty files get an all-zero root hash.

Dependencies and integration points: Depends on `lib_private.h`, hash algorithm backends, UAPI descriptor layout, and public callbacks. The CLI `digest`, `sign`, `enable`, and tests rely on this exact digest format.

Risks and test signals: Risks include off-by-one tree levels, block-size validation, salt padding, callback ordering, and descriptor endian encoding. Strong signals are known-answer digest tests, metadata callback tests, empty-file vectors, and error propagation from read/callback failures.
