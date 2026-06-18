# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portdat.h

This header defines KFS on-disk structures, in-memory core structures, constants, and error codes.

Key on-disk structures:
- `Qid9p1`: 32-bit path plus version.
- `Dentry`: fixed 28-byte name, uid/gid, mode flags, qid, size, direct blocks, indirect blocks, atime, mtime.
- `Tag`: block trailer tag and owner path.
- `Super1`, `Fbuf`, and `Superb`: superblock and freelist state.

Key in-memory structures:
- `Device`, `Filter`, `Filta`, `Tlock`, `File`, `Filsys`, `Hiob`, `Iobuf`, `Uid`, and `Wpath`.

Constants:
- `NAMELEN`, `NDBLOCK`, `MAXDAT`, `NTLOCK`.
- Dentry flags `DALLOC`, `DDIR`, `DAPND`, `DLOCK`, permission bits.
- KFS error enum and max error.
- Block tags `Tsuper`, `Tdir`, `Tind1`, `Tind2`, `Tfile`, `Tfree`, etc.
- Buffer flags `Bread`, `Bprobe`, `Bmod`, `Bimm`, `Bres`.
- Old open modes and checker flags.
- Extern declarations for block-size-derived globals.

Role:
- The most important KFS ABI file: changing its “DONT TOUCH” structures changes disk format.
