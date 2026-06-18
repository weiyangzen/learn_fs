# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mount.h

Purpose: Defines `mount(2)` and `umount2(2)` flags plus userland prototypes.

Key definitions:
- Mount flags: read-only, old/new mount ABI, nosuid, remount, notrunc, overlay, option string, global, forced unmount, omit mnttab.
- Kernel-internal domount flags: sysspace, nosplice, nocheck.
- `MS_CRYPT` for loading encryption keys before mount.
- `MS_MASK`, `MS_UMOUNT_MASK`.
- `MAX_MNTOPT_STR`.

Userland APIs:
- `mount()`
- `umount()`
- `umount2()`

Important detail: `MS_CRYPT` is documented as not being seen by the kernel, avoiding glibc compatibility issues.

Relevance to subset A: Direct filesystem mount ABI.
