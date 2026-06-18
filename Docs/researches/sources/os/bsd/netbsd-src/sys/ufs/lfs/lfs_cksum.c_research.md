# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_cksum.c

Read completely: 117 lines.

Implements LFS checksum helpers shared by kernel and non-kernel builds.

Functions:
- `lfs_cksum_part()` masks the length down to a 16-bit boundary and XORs successive 16-bit words into a running 32-bit sum.
- `cksum()` computes a complete checksum by calling `lfs_cksum_part()` with an initial zero and then `lfs_cksum_fold()`.
- `lfs_sb_cksum()` computes an LFS superblock checksum over the active 32-bit or 64-bit disk superblock variant up to, but not including, the checksum field.

Risks and notes:
- The file explicitly calls the checksum simple and suggests using the TCP/IP checksum instead.
- Input must be short-aligned; the function casts directly to `u_int16_t *`.
- `lfs_cksum_fold()` is currently a macro identity in `lfs_extern.h`, so no additional folding is performed.
