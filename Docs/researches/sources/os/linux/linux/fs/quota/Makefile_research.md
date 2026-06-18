# File Research: sources/os/linux/linux/fs/quota/Makefile

## Role

Build rules for the quota subsystem.

## Contents

- `CONFIG_QUOTA`: `dquot.o`
- `CONFIG_QFMT_V1`: `quota_v1.o`
- `CONFIG_QFMT_V2`: `quota_v2.o`
- `CONFIG_QUOTA_TREE`: `quota_tree.o`
- `CONFIG_QUOTACTL`: `quota.o` and `kqid.o`
- `CONFIG_QUOTA_NETLINK_INTERFACE`: `netlink.o`

## Research Notes

The Makefile keeps generic dquot logic, syscall/control logic, format handlers, tree storage, and netlink warnings independently selectable.
