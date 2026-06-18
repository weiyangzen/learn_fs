# File Research: sources/os/linux/linux/fs/nfsd/netlink.h

Read completely: 32 lines.

Auto-generated header for the NFSD generic netlink family.

Key responsibilities:
- Declares shared nested policies for socket and version attributes.
- Declares NFSD netlink command handlers for RPC status dump and thread/version/listener/pool-mode get/set operations.
- Declares the global `nfsd_nl_family`.

Dependencies:
- Includes generic netlink headers and UAPI `linux/nfsd_netlink.h`.

Notable risks:
- Generated from the NFSD YNL spec; handler prototypes must stay synchronized with generated operation entries.
