# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/chk.c

This file implements the KFS consistency checker and repair logic used by the `check` console command.

Key behavior:
- `check` takes a `Filsys` and check flags, locks the filesystem, reads the superblock, allocates bitmaps for block and qid tracking, walks from the root, optionally rebuilds the free list, and reports summary counts.
- `fsck` recursively validates dentries, names, qids, direct blocks, indirect blocks, and double-indirect blocks.
- `checkdir` scans directory blocks and recurses into allocated entries.
- `checkindir` validates single-indirect blocks and either recurses into directory data or reads file blocks.
- `ckfreelist` walks the on-disk free list and marks free blocks.
- `mkfreelist` rebuilds the free list from unmarked blocks.
- `xtag` reads a block and validates or repairs its tag depending on flags.
- `amark`, `fmark`, and `qmark` detect out-of-range, duplicate, used, free, and qid conflicts.

Repair flags:
- `Cfree`: rebuild freelist.
- `Ctag`: repair tags.
- `Cream`: zero and retag bad blocks.
- `Cbad`: delete redundant block references.
- `Ctouch`: rewrite touched old blocks.
- `Crdall`, `Cpdir`, `Cpfile`, `Cquiet`: read/print/report modifiers.

Dependencies:
- Relies on `getbuf`, `putbuf`, `checktag`, `settag`, `getdir`, `addfree`, and global block-size variables.
- Uses `cprint` so output goes to the KFS command channel.

Notable detail:
- Uses a fixed-depth dentry scratch allocator with `MAXDEPTH`; overly deep trees are reported and not fully traversed.
