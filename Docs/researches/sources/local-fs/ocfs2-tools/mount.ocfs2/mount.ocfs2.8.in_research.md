# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.8.in

Manual page for the OCFS2 mount helper.

It documents invocation through `mount(8)`, OCFS2-specific and common mount options, including `_netdev`, atime modes, ACLs, xattrs, commit interval, data ordering, error handling, flock coherency, allocation reservations, `inode64`, `nocluster`, interruptibility, and read-only/read-write modes.

The notes emphasize clustered mount prerequisites: the cluster stack must be online, mount/unmount can wait on DLM activity, startup mounting is coordinated with `o2cb` and `ocfs2` init services, and failure details are expected in `dmesg`.
