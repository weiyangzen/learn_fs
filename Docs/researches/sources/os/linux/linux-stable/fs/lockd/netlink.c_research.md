# File Research: sources/os/linux/linux-stable/fs/lockd/netlink.c

Generated Generic Netlink family definition for lockd configuration.

Key points:
- Generated from `Documentation/netlink/specs/lockd.yaml`.
- Defines policy for `LOCKD_CMD_SERVER_SET` attributes:
  - gracetime: `NLA_U32`
  - TCP port: `NLA_U16`
  - UDP port: `NLA_U16`
- Registers split ops for:
  - `LOCKD_CMD_SERVER_SET` using `lockd_nl_server_set_doit`, admin permission required.
  - `LOCKD_CMD_SERVER_GET` using `lockd_nl_server_get_doit`.
- Exports `lockd_nl_family` with `netnsok = true`, `parallel_ops = true`, and lockd family name/version.
