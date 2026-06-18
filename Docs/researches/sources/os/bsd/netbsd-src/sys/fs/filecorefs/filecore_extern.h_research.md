# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_extern.h

Read completely: 113 lines.

Declares kernel-private FileCoreFS mount state and shared prototypes. `struct filecore_mnt` stores the mount/device, block size and shift, map location, ids per zone, id mask, block count, mount uid/gid/policy flags, and cached disc record.

Defines `VFSTOFILECORE()` and block offset/number/size macros used by vnode read and bmap code. It also declares the node pool, VFS prototypes, vnode op vector, boot-block checksum, mapped read, and map translation helpers.
