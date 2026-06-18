# File Research: sources/os/linux/linux/fs/nfsd/netlink.c

Read completely: 116 lines.

Auto-generated generic netlink family definition for NFSD administrative control.

Key responsibilities:
- Defines nested attribute policies for server sockets and protocol versions.
- Defines command-specific policies for setting threads, versions, listeners, and pool mode.
- Registers split generic-netlink operations for RPC status dump, thread set/get, version set/get, listener set/get, and pool mode set/get.
- Marks mutating operations with `GENL_ADMIN_PERM`; dump/get operations have command capability flags.
- Defines the `nfsd_nl_family` with name/version from UAPI, netns support, parallel ops, module owner, and operation table.

Dependencies:
- Generated from `Documentation/netlink/specs/nfsd.yaml`.
- Depends on handlers declared in `netlink.h` and UAPI constants in `linux/nfsd_netlink.h`.

Notable risks:
- This file is generated; manual edits would be overwritten by `tools/net/ynl/ynl-regen.sh`.
- Policy definitions are the kernel-side validation boundary for NFSD netlink control messages.
