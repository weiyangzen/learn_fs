# sources/test-tools/strace/bundled/linux/include/uapi/linux/unix_diag.h

## Purpose

Defines netlink diagnostic ABI for Unix-domain sockets. strace uses it to decode `SOCK_DIAG_BY_FAMILY` requests and responses for `AF_UNIX` sockets.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. `struct unix_diag_req` carries family, protocol, state mask, inode filter, show mask, and cookie. Show flags include `UDIAG_SHOW_NAME`, `VFS`, `PEER`, `ICONS`, `RQLEN`, `MEMINFO`, and `UID`. `struct unix_diag_msg` is the base response with family, type, state, inode, and cookie. Attribute ids are `UNIX_DIAG_NAME`, `VFS`, `PEER`, `ICONS`, `RQLEN`, `MEMINFO`, `SHUTDOWN`, and `UID`. Payload structs include `unix_diag_vfs` and `unix_diag_rqlen`.

## Control Flow, State, and Integration

Runtime flow is netlink diagnostic request and dump of kernel Unix socket table state. Persistent state is live socket names, VFS inode data, peer links, pending connection inodes, receive/write queue lengths, memory info, shutdown state, and UID.

## Risks and Test Signals

Risks include confusing abstract socket names with filesystem paths, handling optional attributes only when requested, and stale peer/socket state during dumps. Test signals include show-mask decoding, base message formatting, VFS and queue payloads, and graceful handling of missing optional attributes.
