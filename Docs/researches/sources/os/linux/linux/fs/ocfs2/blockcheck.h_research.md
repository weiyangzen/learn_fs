# File Research: sources/os/linux/linux/fs/ocfs2/blockcheck.h

Public declarations for OCFS2 metadata checksum/ECC support.

Defines:
- `struct ocfs2_blockcheck_stats`: spinlock-protected counters for checked blocks, checksum failures, ECC recoveries, plus optional debugfs directory state.

Declares:
- High-level metadata ECC APIs gated by filesystem feature state.
- Low-level compute/validate APIs for single buffers and buffer_head arrays.
- Debugfs install/remove hooks.
- Hamming encode/fix helpers for single or multi-hunk buffers.

Usage expectations:
- Callers pass disk-format data.
- Validation APIs may mutate the data buffer when ECC repair is attempted.
- Stats are optional; all increment helpers tolerate `NULL`.
