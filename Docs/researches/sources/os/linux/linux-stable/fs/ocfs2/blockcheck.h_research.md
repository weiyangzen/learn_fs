# File Research: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.h

## Summary
Declares OCFS2 block integrity APIs and the statistics structure used by `blockcheck.c`.

## Main Responsibilities
- Define `struct ocfs2_blockcheck_stats` counters and optional debugfs parent.
- Declare high-level metadata ECC compute/validate helpers.
- Declare low-level block and buffer-head check helpers.
- Declare debugfs install/remove routines.
- Declare Hamming encode/fix primitives and block wrappers.

## Key Interfaces
- `ocfs2_blockcheck_stats` tracks checks, checksum failures, and ECC recoveries.
- `ocfs2_compute_meta_ecc()` and `ocfs2_validate_meta_ecc()` operate on one metadata block.
- `_bhs` variants operate on multi-buffer metadata.
- `ocfs2_hamming_encode()` and `ocfs2_hamming_fix()` support incremental hunks.

## Risks
The header exposes both low-level and high-level APIs; callers need to choose the feature-gated metadata wrappers unless they intentionally bypass mount feature checks.
