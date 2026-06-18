# File Research: sources/os/linux/linux/fs/lockd/netlink.c

Purpose: Auto-generated generic netlink family definition for lockd server configuration commands.

Key functionality:
- Defines policy for `LOCKD_CMD_SERVER_SET` attributes: grace time, TCP port, UDP port.
- Registers split ops for `LOCKD_CMD_SERVER_SET` and `LOCKD_CMD_SERVER_GET`.
- Requires admin permission for set operations.
- Defines `lockd_nl_family` with namespace support and parallel ops enabled.

Dependencies and integration:
- Includes generated `netlink.h` and UAPI `linux/lockd_netlink.h`.
- Handler implementations `lockd_nl_server_set_doit()` and `lockd_nl_server_get_doit()` are declared elsewhere in this generated interface.

Risk notes:
- File is generated from `Documentation/netlink/specs/lockd.yaml`; manual edits are not durable.
- Policy bounds are tied to UAPI enum values.
