# File Research: sources/os/linux/linux/fs/smb/client/netlink.c

## Purpose
Registers the CIFS generic netlink family used for server witness notification messages from userspace to the kernel SMB client.

## Main Interfaces
- `cifs_genl_family` defines the generic netlink family, attributes, operations, and multicast groups.
- `cifs_genl_init()` registers the family.
- `cifs_genl_exit()` unregisters the family.

## Main Contents
The file defines `cifs_genl_policy` for witness registration, names, share names, IP sockaddr payloads, notify flags, Kerberos auth flag, credentials, domain name, notification type, resource state, and resource name. It defines one admin-permission operation, `CIFS_GENL_CMD_SWN_NOTIFY`, dispatched to `cifs_swn_notify()`, and one net-admin multicast group.

## Integration Points
Depends on UAPI definitions in `linux/cifs/cifs_netlink.h`, local `netlink.h`, CIFS globals/debug, and server witness notification logic in `cifs_swn.h`.

## Risks And Review Focus
- Attribute policy must stay synchronized with the UAPI enum.
- The notification command is privileged through generic netlink admin permission and multicast group capability flags.
- Registration/unregistration errors are logged but otherwise simple lifecycle events.
