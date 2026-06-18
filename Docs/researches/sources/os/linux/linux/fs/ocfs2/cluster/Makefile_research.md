# File Research: sources/os/linux/linux/fs/ocfs2/cluster/Makefile

Build rules for the OCFS2 cluster/nodemanager module.

Behavior:
- Builds `ocfs2_nodemanager.o` when `CONFIG_OCFS2_FS` is enabled.
- Links object components: `heartbeat.o`, `masklog.o`, `sys.o`, `nodemanager.o`, `quorum.o`, `tcp.o`, and `netdebug.o`.

Significance:
- The cluster support is packaged as the nodemanager module but includes heartbeat, network transport, quorum, sysfs, and debug components.
