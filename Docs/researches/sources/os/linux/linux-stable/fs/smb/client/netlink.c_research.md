# File Research: sources/os/linux/linux-stable/fs/smb/client/netlink.c

Read status: complete.

## Purpose

Defines and registers the CIFS generic netlink family used for server witness notification support.

## Main Responsibilities

- Define generic netlink attribute validation policy for CIFS witness registration and notification data.
- Register the witness notification command.
- Define the witness multicast group.
- Provide module init/exit helpers for generic netlink family registration.

## Important Contents

- `cifs_genl_policy`
  - Attribute policy for SWN registration id, net/share names, IP sockaddr storage, notify flags, Kerberos auth flag, username/password/domain, notification type, resource state, and resource name.

- `cifs_genl_ops`
  - Registers `CIFS_GENL_CMD_SWN_NOTIFY` with admin permission and dispatches to `cifs_swn_notify`.

- `cifs_genl_mcgrps`
  - Defines the `CIFS_GENL_MCGRP_SWN` multicast group with `GENL_MCAST_CAP_NET_ADMIN`.

- `cifs_genl_family`
  - Generic netlink family object using `CIFS_GENL_NAME`, `CIFS_GENL_VERSION`, policy, ops, and multicast group.

- `cifs_genl_init()` / `cifs_genl_exit()`
  - Register and unregister the family, logging VFS errors on failure.

## Dependencies

- Uses Linux generic netlink, UAPI CIFS netlink definitions, CIFS debug logging, CIFS global state, and witness notification code from `cifs_swn.h`.

## Notable Behaviors

- Notification command requires administrative permission.
- String attributes use netlink string policy; IP uses fixed `sockaddr_storage` length.
