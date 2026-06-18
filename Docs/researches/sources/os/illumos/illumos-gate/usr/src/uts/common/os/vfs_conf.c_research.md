# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vfs_conf.c

Defines the static VFS switch table for built-in filesystem type names and initialization hooks.

Key responsibilities:
- Provides `vfssw[]`, the filesystem switch array indexed by filesystem type number.
- Reserves stable positions for built-in filesystems including `specfs`, `ufs`, `fifofs`, `namefs`, `proc`, `nfs`, `zfs`, `hsfs`, `lofs`, `tmpfs`, `pcfs`, `swapfs`, `devfs`, `ctfs`, `objfs`, `sharefs`, `dcfs`, and `smbfs`.
- Installs `swapinit` as the initialization hook for `swapfs`.
- Exports `nfstype` as the array length.

Important invariant:
- The file warns that entry positions must not be changed because many filesystems pass the filesystem type number into `vfs_make_fsid()`. Reordering can change NFS file handles after a server upgrade and cause clients to see stale file handles.

Filesystem relevance:
- Directly VFS-facing. This table ties filesystem names to type numbers and therefore affects mount behavior, filesystem IDs, exported file handles, and code such as label resolution that consults `vfssw[fstype].vsw_name`.
