# File Research: sources/os/linux/linux/fs/smb/server/ksmbd_netlink.h

This header is the userspace ABI between the kernel KSMBD server and the IPC daemon over generic netlink.

Main contents:
- Netlink family name/version and maximum field sizes.
- Request/response structures for heartbeat, startup, shutdown, login, extended login groups, share config, tree connect/disconnect, logout, RPC, and SPNEGO/Kerberos authentication.
- Flexible payload layouts for startup interface lists, share veto/path data, RPC payloads, and SPNEGO session-key/AP-REP payloads.
- `ksmbd_event` enum where response event IDs are paired with request IDs.
- Tree connect status enum.
- User, global, share, tree connect, RPC method, RPC status, and config-option flag namespaces.
- `ksmbd_share_config_path()` helper to locate the path after optional veto-list payload data.

This file is ABI-sensitive: structure packing, field widths, payload order, and flag values must match `ksmbd-tools`.
