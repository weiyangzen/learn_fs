# File Research: sources/local-fs/ocfs2-tools/extras/check_metaecc.c

Read coverage: complete file read, 292 lines.

Purpose: standalone diagnostic utility for checking OCFS2 metadata block CRC/ECC state on a device.

Behavior:
- Parses `check_metaecc [-F|--force] <device> <block #>`.
- Opens the OCFS2 volume read-only with `ocfs2_open()`.
- Refuses to continue if the volume lacks the metaecc feature unless `--force` is supplied.
- Reads one raw block and identifies its metadata type by signature: superblock, inode, extent block, group descriptor, xattr block, refcount block, dx root/leaf, or directory trailer.
- Extracts the appropriate `ocfs2_block_check` field, clears it in the temporary buffer, recalculates CRC32, then tries hamming ECC fixup if CRC does not match.
- Prints `PASS`, `ECC Fixup`, or `FAIL` plus calculated CRC/ECC values.

Important dependencies: `libocfs2`, OCFS2 on-disk metadata signatures, byteorder helpers, `crc32_le()`, `ocfs2_hamming_encode_block()`, and `ocfs2_hamming_fix_block()`.

Risk notes:
- The program mutates only its in-memory block buffer, not the device.
- Return handling has a bug-like shape: `ret` is initialized to `1` and is never set to success after a passing check, so the process may still exit nonzero.
- Unknown metadata signatures are only checked as directory trailers when directory trailers are supported.
