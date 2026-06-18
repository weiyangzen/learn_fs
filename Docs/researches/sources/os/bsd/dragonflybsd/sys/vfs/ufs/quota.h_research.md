# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/quota.h

UFS quota ABI and kernel dquot interface header. It defines user/group quota constants, quotactl command encoding, on-disk quota records, kernel quota cache records, and quota operation prototypes.

Key responsibilities:
- Defines default soft-limit grace periods for inode and disk-block quotas.
- Defines two quota slots, `USRQUOTA` and `GRPQUOTA`, and default quota file naming conventions.
- Defines `QCMD()` encoding and command values for quota on/off, get quota, set quota, set usage, and sync.
- Defines `struct ufs_dqblk`, the on-disk quota record containing hard/soft block limits, current blocks, hard/soft inode limits, current inodes, and block/inode grace expiry times.
- Under `_KERNEL`, defines `struct ufs_dquot` cache entries with hash/free-list links, flags, type, refcount, id, mount pointer, and embedded quota data.
- Defines dquot flags for locking/wakeup/modified/fake/warned states and shorthand field aliases.
- Defines `NODQUOT`, `FORCE`, `CHOWN`, and `DQREF()` behavior.
- Declares kernel quota functions for allocation checks, initialization, release, inode quota lookup, get/set/use, on/off, sync, and quotactl dispatch.
- Declares userland `quotactl()` when not compiling the kernel.

Dependencies:
- Includes `ufs_types.h`.
- Kernel portion uses queue types and forward declarations for inode, mount, process/thread, credentials, vnode, and ufsmount.

Notable risks:
- `struct ufs_dqblk` is on-disk quota-file format; field width/order changes would break existing quota files.
- Kernel and userland share command encoding, so ABI compatibility matters.
- Quota file vnode arrays in `ufsmount` and inode dquot arrays are sized by `MAXQUOTAS`; increasing quota types affects multiple structures and lookup semantics.
