# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntent.h

Purpose: Defines mount table/vfstab path constants, filesystem type names, and mount option string constants.

Key definitions:
- Paths: `MNTTAB`, `VFSTAB`.
- Filesystem type strings: ZFS, UFS, SMBFS, NFS variants, PCFS, LOFS, HSFS, swap, tmpfs, autofs, mntfs, dev, ctfs, objfs, sharefs.
- Mount option strings: read/write mode, quotas, NFS behavior, suid/device/setuid controls, remount, lookup behavior, automount maps, locking, largefiles, direct I/O, logging, atime/deferred atime, nbmand, xattr, exec, browsing, zone, and many more.

Important detail: This header is mostly string constants shared by mount tooling and consumers, not structure definitions.

Relevance to subset A: Direct filesystem administration ABI support.
