# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_lookup.c

Implements Darwin/XNU pathname resolution: `namei`, component lookup, symlink expansion, mountpoint traversal, resource-fork lookup, legacy volfs path translation, relookup, and lookup tracing.

Key behavior:
- `namei` copies user or kernel pathnames into the embedded path buffer, grows to allocated `MAXPATHLEN`/`MAXLONGPATHLEN` buffers when supported, recognizes `/.nofollow/` and `/.resolve/<flags>/` prefixes, sets `NAMEI_*` policy flags, selects root/current/used starting directories, pins root/start vnodes with usecounts, and drives `lookup` until the path completes or a symlink is expanded.
- Resolve-prefix handling maps userspace policy bits into lookup constraints such as no symlinks, no `..`, local-only mounts, no devfs, immovable media only, unique-path requirements, and no xattrs/named streams.
- `lookup` walks path components using `cache_lookup_path` first, authorizes directory search, handles `.`/`..`, chroot boundaries, `NAMEI_RESOLVE_BENEATH`, `NAMEI_NODOTDOT`, read-only mutation checks, mount crossing, union mounts, compound open handoff, and final parent/leaf iocount ownership.
- Cache and identity maintenance are centralized in `lookup_consider_update_cache`, which updates vnode name/parent identity and enters cache records only when flags, vnode cacheability, non-dot names, and directory generation checks permit it.
- `lookup_handle_found_vnode` consumes filesystem-provided extra path bytes, traverses mountpoints, labels multi-label MAC vnodes, detects symlinks, rejects invalid trailing slashes, hides shadow files from ordinary lookup, audits successful paths, and optionally redirects to named resource-fork lookup.
- `lookup_traverse_mountpoints` follows stacked mounts by acquiring mount crossrefs, honoring forced-unmount/nonblocking behavior, enforcing resolve policies against network, devfs, and removable filesystems, resolving trigger vnodes, and caching the real root vnode/generation after traversal.
- `lookup_handle_symlink` reads link text with `VNOP_READLINK`, enforces `MAXSYMLINKS`, validates combined path length, splices link text with remaining suffix, restarts at root for absolute links, and blocks absolute symlink escapes under `NAMEI_RESOLVE_BENEATH`.
- `lookup_handle_rsrc_fork` maps `/..namedfork/rsrc` style requests to `vnode_getnamedstream`, requiring explicit `CN_ALLOWRSRCFORK` authorization and preserving audit path suffixes.
- Volfs compatibility resolves `/.vol/<fsid>/<ino>[/tail]` through `vfs_getrealpath`, `mount_lookupby_volfsid`, `VFS_ROOT`/`VFS_VGET`, chroot containment checks, and `build_path`, with bounded restart on `ENOENT`.
- `relookup` provides a single-component reacquire helper used after prior lookup state, while `nameidone` frees allocated pathname buffers.
- Kdebug helpers encode lookup path bytes across one or more trace events, and `lookup_compound_vnop_post_hook` mirrors audit/cache/trace side effects after compound VNOPs.

Dependencies:
- Uses vnode, mount, namecache, `VNOP_LOOKUP`, `VNOP_READLINK`, `VFS_ROOT`, `VFS_VGET`, audit, MACF, kdebug, trigger, union mount, named-stream, and volfs infrastructure.
- Depends on `struct nameidata`, `struct componentname`, vnode iocount/usecount rules, process root/cwd state, and `rootvnode_rw_lock`.

Research notes:
- This file is the VFS namespace policy choke point for Darwin path lookup. It combines correctness-sensitive lifetime handling with security policy flags and filesystem callbacks.
- The code carefully distinguishes iocounts from usecounts, especially around root/start directories and symlink restarts.
- Several behaviors are compile-time optional (`CONFIG_VOLFS`, `CONFIG_TRIGGERS`, `CONFIG_UNION_MOUNTS`, `NAMEDRSRCFORK`, `NAMEDSTREAMS`, `CONFIG_MACF`) and should be considered when comparing XNU builds.
