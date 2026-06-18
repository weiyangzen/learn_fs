# File Research: sources/local-fs/ocfs2-tools/libocfs2/blockcheck.c

Implements metadata checksum and ECC logic for OCFS2 userspace.

The Hamming encoder maps set data bits into 1-based Hamming code positions, reserving power-of-two parity bits, and XORs code-bit positions to produce parity. It supports incremental hunks through `ocfs2_hamming_encode()` and whole blocks through `ocfs2_hamming_encode_block()`. Fix-up functions flip the data bit indicated by an ECC syndrome unless the error is in a parity bit or outside the current hunk.

CRC32 uses the generated little-endian table from `crc32table.h`, with alignment handling and endian-dependent update macros. `ocfs2_block_check_compute()` zeroes the embedded check field, computes CRC32 and Hamming ECC over disk-endian data, and writes little-endian check values. `ocfs2_block_check_validate()` saves existing check values, zeroes the check field, validates CRC, attempts Hamming single-bit repair on mismatch, retries CRC, restores the check field, and returns `OCFS2_ET_BAD_CRC32` if still invalid.

Top-level `ocfs2_compute_meta_ecc()` and `ocfs2_validate_meta_ecc()` gate the work on the filesystem metadata-ECC feature and the `OCFS2_FLAG_NO_ECC_CHECKS` flag. Debug code benchmarks CRC and several Hamming variants against file input.
