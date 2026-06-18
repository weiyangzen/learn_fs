# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/Makefile

## Summary
Builds the OCFS2 cluster support module object when `CONFIG_OCFS2_FS` is enabled.

## Main Responsibilities
- Add `ocfs2_nodemanager.o` to the OCFS2 build.
- Compose that object from heartbeat, masklog, sysfs, nodemanager, quorum, tcp, and netdebug sources.

## Key Interfaces
- `obj-$(CONFIG_OCFS2_FS) += ocfs2_nodemanager.o`
- `ocfs2_nodemanager-objs := heartbeat.o masklog.o sys.o nodemanager.o quorum.o tcp.o netdebug.o`

## Risks
This file defines module composition boundaries. Missing an object here would silently remove cluster subsystem behavior from the OCFS2 module.
