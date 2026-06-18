# File Research: sources/os/linux/linux/fs/jffs2/symlink.c

## Role

Defines Linux inode operations for JFFS2 symbolic links.

## Key Responsibilities

- Exposes `jffs2_symlink_inode_operations`.
- Uses `simple_get_link` because symlink target text is cached in `inode->i_link`/JFFS2 inode state by inode read/setup code.
- Reuses `jffs2_setattr` for metadata changes.
- Reuses `jffs2_listxattr` for xattr listing.

## Important Interactions

- Symlink targets are read and cached by `readinode.c`.
- Attribute updates route through common JFFS2 setattr logic.
- Xattr listing routes through the shared xattr subsystem.

## Invariants and Risks

- This file contains only the operation table; correctness depends on inode setup and cached symlink target lifetime elsewhere.
