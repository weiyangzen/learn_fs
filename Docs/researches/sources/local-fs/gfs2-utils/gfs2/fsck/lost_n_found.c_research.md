# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.c

## Purpose
Creates or locates `lost+found` and reconnects orphaned or damaged inodes into it during fsck repairs.

## Main Elements
- `add_dotdot()`: rewrites an orphan directory’s `..` entry to point at `lost+found`, decrementing the old parent’s counted/on-disk link when appropriate.
- `make_sure_lf_exists()`: creates or finds root `lost+found`, updates root/lost+found link accounting, marks the new dinode in fsck/rgrp bitmaps, and marks the directory connected.
- `add_inode_to_lf()`: chooses a `lost_*` name by inode mode, adds a directory entry in `lost+found`, updates counted links, and writes the lost+found dinode.

## Dependencies And Integration
Uses global `lf_dip` and `lf_was_created` from `main.c`, directory mutation APIs from libgfs2, link accounting from `link.c`, directory tree state, and bitmap setting from `metawalk.h`. Invoked by later passes when disconnected inodes/directories must be preserved.

## Risk Notes
Directory reconnection changes parentage and link counts. The old `..` target is checked by formal inode number before decrementing, which limits damage from stale parent references.
