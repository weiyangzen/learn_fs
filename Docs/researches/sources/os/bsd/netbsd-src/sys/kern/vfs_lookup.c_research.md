# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_lookup.c

Read completely: 2349 lines.

Implements NetBSD pathname lookup: path buffer management, `namei()`, namecache fast-forwarding, mount traversal, symlink handling, emulation-root retry, NFS server lookup variants, `relookup()`, and simple lookup wrappers.

Path and helper infrastructure:
- `symlink_magic()` expands optional magic symlink tokens such as machine, hostname, OS release, emulation name, domain, uid/gid, and real uid/gid.
- `namei_hash()` computes namecache-compatible hashes while optionally finding the next path separator.
- `struct pathbuf` owns a pathname buffer and an optional saved copy of the original string.
- `pathbuf_create()`, `pathbuf_copyin()`, `pathbuf_maybe_copyin()`, `pathbuf_assimilate()`, and `pathbuf_destroy()` centralize pathname buffer ownership.
- `pathbuf_stringcopy_get/put()` support retry paths where lookup mutates the active path buffer.

Namei state and startup:
- `struct namei_state` wraps `nameidata`, component state, cache policy, readonly state, slash count, retry state, and root-reference bookkeeping.
- `namei_getstartdir()` chooses the start vnode from absolute root, current directory, `at` directory, chroot root, or emulation root.
- It references root and emulation root during lookup so concurrent `chroot` changes cannot invalidate them.
- `namei_getstartdir_for_nfsd()` provides a reduced start-directory path for NFS server callers.
- `namei_start()` validates nonempty paths, computes path length, obtains the start directory, rejects non-directory starts, and emits ktrace records for normal lookups.

Component lookup flow:
- `lookup_parsepath()` delegates component parsing to `VOP_PARSEPATH()`, updates `ni_next`, tracks trailing slashes, sets `REQUIREDIR`, `ISLASTCN`, `MAKEENTRY`, and `ISDOTDOT`.
- `lookup_lktype()` chooses shared vs exclusive directory locks based on filesystem shared-lookup support and whether the operation can modify the directory.
- `lookup_once()` handles one filesystem lookup, including `..` chroot containment, mountpoint-up traversal, VOP lookup, `ENOLCK` retry with exclusive lock, union mount fallback, creation via `EJUSTRETURN`, and parent locking.
- `lookup_crossmount()` descends through mounted-on directories using mount-root cache entries when possible and `VFS_ROOT()` under filesystem transaction protection otherwise.
- `lookup_fastforward()` uses namecache node locks to traverse easy cached components without repeated vnode references or locks, rolling back to filesystem lookup when unsupported.

Symlink and full-path behavior:
- `namei_follow()` enforces `MAXSYMLINKS`, optionally checks `VEXEC` on symlinks under `MNT_SYMPERM`, reads the link target, performs magic substitution when enabled, splices remaining path text, and restarts from root or emulation root for absolute links.
- `namei_oneroot()` drives the full loop: fast-forward/cache lookup, fallback lookup, mount crossing, symlink following, required-directory checks, final parent/leaf lock handling, readonly operation checks, and emulation-root normalization.
- It handles `NONEXCLHACK` for open-with-create-but-not-exclusive cases that should tolerate missing parent vnode returns across mountpoints.
- `namei_tryemulroot()` retries from the real root when an emulation-root lookup fails in retry-eligible cases.

External entry points:
- `namei()` is the main public interface.
- `lookup_for_nfsd()` supports NFS server lookups with forced current directory, optional no-follow behavior, and magic symlink inhibition.
- `lookup_for_nfsd_index()` performs a constrained single-component WebNFS index lookup.
- `relookup()` reacquires a previously parsed final component under a locked parent directory.
- `namei_simple_*()` and `nameiat_simple_*()` provide simple kernel/user pathname-to-vnode wrappers with follow/no-follow and emulation-root flags.

Risks and notes:
- This file is highly sensitive to vnode reference, lock, and mount transaction ordering; several comments call out deliberately awkward cases.
- `searchdir` can intentionally become `NULL` after crossing mountpoints, so callers must honor the documented parent-return contract.
- Namecache fast-forwarding is performance-critical but must roll back precisely when references cannot be acquired.
- Magic symlinks expose kernel/process-derived strings inside pathname resolution and are gated by `vfs_magiclinks`.
- Emulation-root retry mutates and restores the path buffer, making saved-path lifetime important.
- NFS server lookup interfaces are special-case compatibility paths and are explicitly marked as candidates for interface cleanup.
