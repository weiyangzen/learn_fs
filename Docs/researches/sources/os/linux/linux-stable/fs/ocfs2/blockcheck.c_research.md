# File Research: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.c

## Summary
Implements OCFS2 metadata block integrity checking with CRC32 plus Hamming-code ECC. It can compute and validate checks for contiguous blocks or multi-buffer metadata, attempt single-bit recovery after CRC failure, and publish optional debugfs counters.

## Main Responsibilities
- Encode Hamming parity over one buffer or multiple data hunks.
- Locate and flip a single bad data bit from stored-vs-computed parity.
- Compute `struct ocfs2_block_check` fields in little-endian disk format.
- Validate checks, restore check fields after validation, and attempt ECC recovery.
- Maintain checked, failed, and recovered counters with spinlock protection.
- Install/remove debugfs statistics files when debugfs is enabled.
- Gate high-level metadata ECC operations on the mounted filesystem feature flag.

## Key Interfaces
- `ocfs2_hamming_encode()`, `ocfs2_hamming_fix()`, and block wrappers are the low-level ECC API.
- `ocfs2_block_check_compute()` and `ocfs2_block_check_validate()` handle one memory block.
- `ocfs2_block_check_compute_bhs()` and `ocfs2_block_check_validate_bhs()` handle arrays of buffer heads.
- `ocfs2_compute_meta_ecc*()` and `ocfs2_validate_meta_ecc*()` are feature-aware filesystem entry points.
- `ocfs2_blockcheck_stats_debugfs_install()` and `_remove()` expose counters.

## Important Behavior
Validation temporarily zeroes the embedded check structure, computes CRC32, and succeeds immediately if CRC matches. On mismatch, it computes Hamming parity, applies the XOR difference as a possible single-bit fix, recomputes CRC, and returns `-EIO` if recovery still fails.

Multi-buffer ECC preserves a continuous bit numbering across buffers by passing each buffer’s bit offset into the Hamming encoder/fixer.

## Risks
ECC correction assumes the failure is within the repairable Hamming model. Multi-bit corruption may not recover and must remain an I/O error. Callers must pass on-disk little-endian data and ensure embedded check fields are correctly zeroed or pointed to by `bc`.
