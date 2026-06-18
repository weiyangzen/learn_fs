# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devmulti.c

This file implements a multi-file “wren” block device backend for KFS.

Key behavior:
- Supports up to `MAXWREN` component files.
- `wrenpartinit` opens each backing file, reads stat length using an old stat-buffer parser, checks per-part magic, and establishes `RBUFSIZE`.
- `wreninit` initializes all component files and switches to multi-wren magic if `nwren > 0`.
- `wrenpartream` writes the magic and block size into each component.
- `wrencheck` validates magic, superblock tag, root directory tag, and root allocation.
- `wrensize` sums component block counts.
- `wrenread` and `wrenwrite` map a logical KFS block across component files, skipping the magic block in later parts.

Dependencies:
- Device dispatch from `dat.c`.
- Uses `ialloc`, `panic`, KFS tags, and `Dentry`.

Notable detail:
- This is an older or alternate backend to `devwren.c`; both define similar `wren*` symbols, so builds select one, not both.
