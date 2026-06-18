# File Research: sources/virtualization/spdk/lib/iscsi/portal_grp.c

Full-file read: 514 lines.

This file implements iSCSI portal and portal-group management, including listener sockets, accept polling, CHAP defaults, redirect address parsing, and JSON output.

Main responsibilities:
- Create/destroy portals and portal groups.
- Normalize wildcard portal addresses: `[*]` to `[::]`, `*` to `0.0.0.0`.
- Prevent duplicate global portal address/port pairs.
- Open listener sockets, add them to SPDK socket groups, accept incoming sockets, and construct iSCSI connections.
- Register/unregister portal groups in `g_iscsi.pg_head`.
- Close/release all portal resources.
- Store portal-group CHAP policy and serialize portal groups to JSON/config JSON.

Important control flow:
- `iscsi_portal_accept` loops on `spdk_sock_accept` until no socket is available; each accepted socket is passed to `iscsi_conn_construct`.
- `iscsi_portal_grp_open` creates a socket group, registers an acceptor poller, optionally pauses it, then opens every portal.
- `iscsi_portal_grp_release` closes sockets/poller/socket group and destroys portals/group.
- `iscsi_parse_redirect_addr` validates numeric host/port with `getaddrinfo`.

Integration points:
- Called by iSCSI RPCs and subsystem shutdown.
- New accepted connections enter the connection layer via `iscsi_conn_construct`.
- Portal groups are mapped into targets by `tgt_node.c`.

Risks and review notes:
- If one portal fails during `iscsi_portal_grp_open`, cleanup is left to caller release paths.
- Duplicate detection compares the input host/port, while wildcard normalization changes stored host strings; edge cases around `*` versus `0.0.0.0` matter.
- `iscsi_portal_grp_close_all` holds `g_iscsi.mutex` while closing groups, which calls socket APIs.

Testing focus:
- Duplicate and wildcard portal creation.
- Partial portal open failure and release.
- Paused portal group start behavior.
- IPv4/IPv6 redirect address validation.
