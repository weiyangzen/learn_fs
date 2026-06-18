# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.c

Main OCFS2 mount helper.

It parses `-v`, `-n`, `-o`, and `-t`, validates the device, mountpoint, and filesystem type, opens the OCFS2 device read-only through libocfs2, and determines whether the mount is clustered, local, hard-read-only, or using the explicit `nocluster` override.

For clustered mounts it initializes the O2CB stack, fills cluster and heartbeat descriptors, performs `o2cb_begin_group_join()` before `mount(2)`, and completes or cleans up the group join afterward. It appends kernel/user options such as `heartbeat=none`, `heartbeat=local`, `heartbeat=global`, or `cluster_stack=<stack>` according to superblock and cluster-stack state.

After a successful mount it optionally lowers local heartbeat I/O priority through `o2hbmonitor`, builds the mtab option string with `_netdev` for clustered mounts, and updates `/etc/mtab` unless `-n` was requested. The risky path is the `nocluster` confirmation, which allows mounting a clustered volume without cluster coordination after a single interactive `Y`.
