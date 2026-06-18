# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_open.c

This file implements quota handle creation/destruction and quota on/off dispatch. `quota_open` calls `statvfs` on any path within the target volume, loads fstab quota metadata, and selects backend mode in a documented order: NFS first, because it uses rquotad instead of kernel quota state; kernel mode if `ST_QUOTA` is set; old quota files if fstab enables quota options; otherwise `EOPNOTSUPP`.

On success it allocates `struct quotahandle`, stores duplicated mountpoint and mount device strings from `statvfs`, records the selected mode, and initializes oldfiles state and fds. Allocation failures preserve errno and free partial state. `quota_getmountpoint` and `quota_getmountdevice` return the stored strings.

`quota_close` closes open user/group quota file descriptors, frees the mount strings, and frees the handle. `quota_quotaon` rejects NFS, calls oldfiles quotaon for oldfiles handles, and calls kernel quotaon for kernel handles. `quota_quotaoff` rejects NFS, rejects oldfiles with `ENOTCONN` because direct oldfiles mode has not quotaon'd through the kernel, and calls kernel quotaoff for kernel handles. Unknown modes return `EINVAL`.
