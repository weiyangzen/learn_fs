# File Research: sources/os/linux/linux-stable/fs/quota/netlink.c

## Purpose
Defines the generic netlink family used by VFS quota code to notify userspace about quota warnings.

## Main Components
- Generic netlink family: `VFS_DQUOT`, version 1.
- Multicast group: `events`.
- Exported notifier: `quota_send_warning()`.

## `quota_send_warning()`
Builds and multicasts a `QUOTA_NL_C_WARNING` message with:
- quota type,
- exceeded quota ID,
- warning type,
- device major/minor,
- current uid as caused-by ID.

Allocation uses `GFP_NOFS` because warnings can be emitted from filesystem write paths where reclaim recursion could deadlock.

## Initialization
`quota_init()` registers the generic netlink family at `fs_initcall` time and logs failure if registration fails.

## Interactions
Called from `dquot.c` warning flushing after quota hard/soft limit transitions.
