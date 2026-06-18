# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1.c

This file implements phase 1: block and inode size validation.

Key behavior:
- Initializes reserved filesystem metadata blocks in `blockmap`.
- Iterates every cylinder group, validates or optionally rebuilds cylinder group headers.
- Determines initialized inode range, with a soft-updates optimization to trim scanning to the highest used inode bitmap bit.
- Allocates `inostathead[c].il_stat` entries for inode state.
- Scans allocated inodes with `getnextinode()` and `checkinode()`.
- Optionally trims UFS2 `cg_initediblk` when `-r` is used.
- Shrinks in-memory inode-state arrays to the actually found inode count when possible.

`checkinode()`:
- Detects partially allocated zero-mode inodes.
- Validates file size, special-file size and rdev, file type, stale direct/indirect pointers beyond file size, and block count.
- Classifies inodes into `USTATE`, `FSTATE`, `FZLINK`, `DSTATE`, `DZLINK`, `DCLEAR`, or `FCLEAR`.
- Caches directories for later passes.
- Scans normal and external-attribute blocks.
- Corrects `di_blocks`.
- Detects file sizes extending beyond the last allocated block and shortens when approved.

`pass1check()`:
- Validates each fragment range.
- Marks bad blocks and duplicate blocks.
- Builds the duplicate list split between unique duplicates and repeated duplicate occurrences.
- Counts allocated blocks and tracks last allocated logical block.
- Enforces `MAXBAD` and `MAXDUP` thresholds.

Important interactions:
- Supplies the authoritative block allocation map used by pass 5.
- Supplies inode state and directory caches used by passes 2 through 4.
- Snapshot descriptors alter handling of `BLK_NOCOPY` and `BLK_SNAP`.
