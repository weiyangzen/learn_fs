# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_getcwd.c

Read completely: 433 lines.

Implements kernel pathname reconstruction for current-working-directory and related containment/path queries. It walks from a leaf vnode up toward a root vnode, using reverse namecache hits when possible and directory scans as fallback.

Parent/name discovery:
- `vfs_getcwd_getcache()` uses `cache_revlookup()` to find a parent vnode and component name, then unlocks the child, locks the parent with `vget()`, and validates the parent's `v_id`.
- On cache miss or invalidation it reacquires the child lock and tells the caller to use the slow path.
- `vfs_getcwd_scandir()` performs `VOP_LOOKUP("..")`, reads parent directory entries with `VOP_READDIR()`, and finds the entry whose file id matches the child vnode.
- It uses `VOP_GETATTR()` to obtain the child's file id and directory block size.
- It retries from offset zero up to three times on NFS-style `EINVAL` cookie failures.
- Directory entries are validated for record length and name bounds before copying names backward into the output buffer.

Common walk:
- `vfs_getcwd_common()` references the requested root and leaf, locks the leaf, then walks upward until it reaches the root, a mount boundary, an error, or a traversal limit.
- It handles mounted filesystem roots by stepping to `mnt_vnodecovered`.
- Optional `GETCWD_CHECK_ACCESS` enforces execute/read access while walking.
- Components are prepended into the caller buffer, with `/` separators inserted as the walk progresses.
- `sys___getcwd()` allocates a bounded temporary buffer, calls the common walker from `fd_cdir`, copies the result to userland, and emits ktrace namei data when enabled.

Risks and notes:
- Correctness depends on careful lock transitions between child and parent vnodes.
- Reverse cache results are advisory and must be validated by vnode generation.
- The fallback directory scan depends on stable file ids and well-formed `struct dirent` records.
- Buffer construction works backward, so off-by-one checks around `bufp`, `bpp`, and separators are important.
- Crossing mount roots requires replacing the current vnode with `mnt_vnodecovered` without leaking references.
