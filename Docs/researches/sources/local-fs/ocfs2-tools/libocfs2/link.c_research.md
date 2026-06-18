# File Research: sources/local-fs/ocfs2-tools/libocfs2/link.c

Creates directory entries in OCFS2 directories.

Main API:
- `ocfs2_link(fs, dir, name, ino, flags)` inserts `name -> ino` into directory inode `dir`. Low three bits of `flags` are used as directory entry file type.

Insertion logic:
- Uses `ocfs2_dir_iterate()` with `OCFS2_DIRENT_FLAG_INCLUDE_EMPTY`.
- `link_proc()` first tries to absorb a following unused directory entry into the current entry.
- If current entry is used and has slack, it shrinks it to minimum size and creates an unused entry in the remaining space.
- If current entry is unused and large enough, it writes inode, name length, name bytes, and file type.
- If no space exists, `ocfs2_expand_dir()` grows the directory, rereads the directory inode, and retries.

Directory trailer support:
- `blockend` is set to either the full block size or `ocfs2_dir_trailer_blk_off(fs)` when directory trailers are present, preventing writes over trailer metadata.

Indexed directory support:
- After insertion into the directory block, if the filesystem supports indexed directories and the directory has `OCFS2_INDEXED_DIR_FL`, it inserts the name into the dx directory index using `ocfs2_dx_dir_insert_entry()`.

Important checks:
- Requires writable filesystem.
- Validates target inode block number against superblock minimum and filesystem block count.
- Does not itself update target inode link count; this is only the directory-entry insertion helper.
