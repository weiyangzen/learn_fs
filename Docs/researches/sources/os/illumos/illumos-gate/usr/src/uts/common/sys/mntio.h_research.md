# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mntio.h

Purpose: Defines private mntfs ioctl commands and request/lookup structures.

Key definitions:
- Ioctls: number of mounts, mounted device list, set/clear tag, show hidden, get mount entry, get extended mount entry, get matching mount.
- Return codes: `MNTFS_EOF`, `MNTFS_TOOLONG`.
- `MAX_MNTOPT_TAG`.

Key structures:
- `mnttagdesc` and 32-bit variant: major/minor, mount point, tag.
- `mntlookup` and 32-bit variant: mount-point offset/pointer, major/minor, inode, fstype.

Important detail: Several commands are marked private and are part of mntfs plumbing rather than a broad stable API.

Relevance to subset A: Directly relevant to in-kernel mount table filesystem behavior.
