# File Research: sources/os/bsd/freebsd-src/sys/sys/mount.h

Defines FreeBSD filesystem mount ABI, VFS mount structures, statfs layouts, mount flags, export structures, VFS operation vectors, VFS registration macros, and mount lifecycle APIs.

Key content:
- Defines `fsid_t`, `fsidcmp`, `struct fid`, `fhandle_t`, and current/legacy `statfs` layouts.
- `struct statfs` contains version, filesystem type, exported flags, block/file counters, read/write counters, vnode list size, name length, owner, fsid, type name, mounted-from name, and mount-on name.
- `_WANT_MOUNT`/kernel section defines mount option lists and `struct vfsopt`.
- `struct mount_pcpu` tracks per-CPU thread-in-op, references, lock references, and write operation counts.
- `struct mount_upper_node` tracks stacked filesystems mounted above a lower filesystem.
- `struct mount` is the core per-mounted-filesystem object: operation counters, flags, pcpu state, root/covered vnodes, vfsops/vfsconf, interlock, vnode lists, write counts, mount options, statfs cache, credentials, private data, export data, MAC label, hash seed, suspension state, rename/export locks, upper/notification lists, deferred-unmount fields, etc.
- Provides vnode iteration macros for all vnodes and lazy vnodes on a mount.
- Provides mount interlock/reference macros.
- Defines mount option name mappings when requested.
- User-visible `MNT_*` flags cover read-only, sync/async, noexec/nosuid, ACL/NFSv4 ACL, union, noatime, clustering, soft updates/SUJ, gjournal, MAC multilabel, automounted, verified, untrusted, named attributes, NFS export/TLS flags, local/quota/root/user/ignore, and command flags.
- Internal `MNTK_*` flags describe unmount, suspend, async filtering, softdep interactions, shared write/lock behavior, I/O page-fault policy, nullfs cache behavior, fast path lookup, buffer cache use, and more.
- Defines VFS sysctl identifiers, sync wait modes, export argument structures, public NFS export state, `struct vfsconf`, userland `xvfsconf`, implementation flags `VFCF_*`, VFS control structures, and `vfsquery`.
- Kernel VFS op typedefs include mount, cmount, unmount, root, quotactl, statfs, sync, vget, fhtovp, checkexp, init/uninit, extattrctl, sysctl, suspension cleanup, lower-vnode notifications, purge, and lockf reporting.
- `struct vfsops` contains the filesystem operation vector plus ABI spares.
- Inline wrappers dispatch `VFS_*` operations and optionally trace mount.
- `VFS_SET` declares a filesystem module using `module.h`.
- Declares large VFS API surface for mount argument building, option parsing, exporting, busy/unbusy, root mount, notification, refs, mount allocation/destruction, syncer vnodes, VFS registration, default ops, suspend/resume all filesystems, operation barriers, and per-CPU operation counters.
- Userland declarations include file-handle APIs, `statfs`/`fstatfs`/`getfsstat`/`getmntinfo`, `mount`, `nmount`, `unmount`, and `getvfsbyname`.

Research relevance:
- This is the primary VFS mount contract for FreeBSD. It defines how filesystem modules register, mount, export, report stats, synchronize, and interact with vnodes.
- It is central to local filesystems, network filesystems, stacked filesystems, jail-aware exports, lock reporting, and mount lifecycle.
- Integrates with `module.h`, `lockmgr.h`, `lock.h`, vnode code, MAC labels, NFS export structures, and per-CPU operation accounting.

Cautions:
- Comments explicitly warn that changing `statfs`, `mount`, `MNT_*`, or `MNTK_*` requires updating DDB mount display code.
- User-visible flags, command flags, and internal flags share names/prefixes but have distinct semantics.
- Some old flags intentionally collide in different syscall contexts.
- Per-CPU VFS op enter/exit relies on critical sections and atomic fences; misuse can break unmount/drain invariants.
