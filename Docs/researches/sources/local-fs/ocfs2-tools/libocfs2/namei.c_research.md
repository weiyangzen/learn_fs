# File Research: sources/local-fs/ocfs2-tools/libocfs2/namei.c

Implements pathname resolution over OCFS2 directory lookup primitives.

Main APIs:
- `ocfs2_namei(fs, root, cwd, name, inode)` resolves a pathname without following the final component if it is a symlink.
- `ocfs2_namei_follow(fs, root, cwd, name, inode)` resolves and follows the final symlink.
- `ocfs2_follow_link(fs, root, cwd, inode, res_inode)` follows a specific symlink inode.

Resolution model:
- `dir_namei()` walks all parent path components relative to `cwd` or `root` if the path begins with `/`.
- Each intermediate component is looked up with `ocfs2_lookup()` and passed through `follow_link()`.
- `open_namei()` resolves the containing directory and final basename, handles trailing slash as a special case, and optionally follows the final symlink.

Symlink handling:
- `follow_link()` reads the inode; if it is not a symlink, it returns the inode unchanged.
- Symlink loop depth is capped after five follows with `OCFS2_ET_SYMLINK_LOOP`.
- The implementation only handles symlinks backed by extents: it requires nonzero clusters and an extent-list record, reads the first target block, and resolves the target with `open_namei()`.
- Fast symlink handling is not present here, despite `inode.c` recognizing fast symlinks as non-extent inodes.

Dependencies:
- Uses `ocfs2_lookup()`, inode reads, extent-list fields, block reads, and block-buffer allocation.
- Ported from e2fsprogs namei logic with OCFS2 inode/block semantics.
