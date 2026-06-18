# File Research: sources/os/linux/linux/fs/ocfs2/blockcheck.c

Implements metadata CRC32 and Hamming-code ECC for OCFS2 metadata blocks and buffer_head lists.

Core algorithms:
- `calc_code_bit()` maps 0-based data bit offsets into 1-based Hamming-code positions, skipping parity positions.
- `ocfs2_hamming_encode()` computes parity over one hunk and supports chained calls across multiple buffers.
- `ocfs2_hamming_fix()` flips the data bit identified by a parity mismatch, ignoring pure parity-bit errors and hunks not containing the bad bit.
- Block wrappers provide single-buffer convenience APIs.

Block check APIs:
- `ocfs2_block_check_compute()` zeroes the embedded `struct ocfs2_block_check`, computes CRC32 and ECC over on-disk-format data, and stores little-endian results.
- `ocfs2_block_check_validate()` verifies CRC first, then attempts one-bit ECC repair and rechecks CRC.
- `_bhs` variants compute and validate checks over multiple buffer_heads as one logical block stream.
- High-level `ocfs2_compute_meta_ecc*()` and `ocfs2_validate_meta_ecc*()` call the low-level routines only when the mounted filesystem advertises metadata ECC.

Debug/observability:
- Optional debugfs support exposes `blocks_checked`, `checksums_failed`, and `ecc_recoveries`.
- Stats increments are spinlock-protected and log wraparound.

Important invariants:
- Metadata passed in must already be in on-disk endian form.
- The check structure is expected to be inside the data or equivalent fields must already be zeroed by the caller.
- ECC is asserted to fit in 16 bits because OCFS2 ECC-covered metadata structures are no larger than 4 KiB.
- Failed ECC repair returns `-EIO` after restoring the original check fields.
