# File Research: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_nodemanager.h

Userspace/kernel shared nodemanager constants.

Defines:
- `O2NM_API_VERSION` as 5.
- Maximum nodes: 255.
- Invalid node number: 255.
- Maximum node/host/group/cluster name length: 64.
- Maximum global heartbeat regions: 32, with compatibility warning.

Usage:
- Included by nodemanager and heartbeat headers.
- Exposed through sysfs interface revision in `sys.c`.
