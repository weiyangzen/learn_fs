# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/tlabel.c

Implements Trusted Extensions label allocation/refcounting and file-label resolution for local, loopback, ZFS, and NFS filesystems.

Key responsibilities:
- Initializes global label state in `label_init()`, including the `tslabel_cache`, `l_admin_low`, and `l_admin_high`.
- Allocates, duplicates, holds, releases, compares, and extracts DOI/basic-label data from `ts_label_t`.
- Resolves a file's effective label through vnode, VFS, zone, ZFS dataset, NFS server, CIPSO, and lofs export context.
- Exposes `getlabel()` and `fgetlabel()` syscall helpers that copy a file label to userland.

Important paths:
- `getflabel_cipso()` infers a remote CIPSO NFS resource label by matching exported NFS resource paths to local zones, relying on TX convention that zone names and paths match between server and client.
- `getflabel_zfs()` reads the ZFS `mlslabel` dataset property with `dsl_prop_get()`, ignores the default property value, converts a hex label, and returns a new `ts_label_t`.
- `getflabel_nfs()` looks up the NFS server transport endpoint in the trusted-network database, delegates CIPSO peers to `getflabel_cipso()`, and uses the peer default label for unlabeled hosts.
- `getflabel()` unwraps real vnodes with `VOP_REALVP()`, handles NFS first, fast-paths non-global-zone non-lofs files to the zone label, falls back to path-based zone lookup, checks ZFS explicit labels, and distinguishes global-zone admin-high files from admin-low files exported into non-global zones through lofs.
- `cgetlabel()`, `getlabel()`, and `fgetlabel()` are the user-visible copyout wrappers around `getflabel()`.

Locking and lifetime:
- `ts_label_t` lifetime is atomic reference-counted.
- VFS resources and mountpoint strings are held through `refstr_t`; VFS structures are held only when their mountpoint can safely be referenced.
- Zone references are acquired with `zone_hold()` / `zone_find_by_any_path()` and released with `zone_rele()`.
- The global VFS list is protected with `vfs_list_read_lock()` while scanning lofs exports.

Filesystem relevance:
- This file is directly VFS-facing. It determines security labels for file objects by combining vnode identity, filesystem type names in `vfssw`, mount resources, ZFS properties, NFS server trust metadata, loopback mounts, and zone path ownership.
