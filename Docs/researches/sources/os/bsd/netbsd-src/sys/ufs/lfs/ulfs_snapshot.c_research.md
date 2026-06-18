# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_snapshot.c

Read completely: 86 lines.

Contains only the ULFS snapshot last-name-removal hook for LFS.

Behavior:
- `ulfs_snapgone(struct inode *ip)` ignores its inode argument and immediately panics with `"reached ulfs_snapgone\n"`.

Context:
- The file is derived from FFS snapshot code but does not implement snapshot machinery for LFS.
- `ulfs_dirremove()` and `ulfs_dirrewrite()` call `ulfs_snapgone()` if an inode with `SF_SNAPSHOT` reaches link count zero.

Risks and notes:
- Any code path that actually removes the last name from an LFS snapshot inode will panic.
- This appears to be an intentional unsupported-snapshot guard rather than functional snapshot cleanup.
