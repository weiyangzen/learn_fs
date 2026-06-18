# sources/user-network-fs/samba/source4/ntvfs/cifs/vfs_cifs.c

## Purpose

`vfs_cifs.c` implements the source4 NTVFS `cifs` backend, a CIFS-on-CIFS proxy filesystem. It accepts NTVFS file-share operations from Samba clients and forwards them to an upstream SMB/CIFS server using the raw SMB client library.

## Important APIs, Types, and Functions

The module init entry point is `ntvfs_cifs_init()`. Runtime state is `struct cvfs_private`, `struct cvfs_file`, and `struct async_info`. Important operations include `cvfs_connect()`, `cvfs_disconnect()`, `cvfs_open()`, `cvfs_close()`, `cvfs_read()`, `cvfs_write()`, `cvfs_lock()`, `cvfs_notify()`, `cvfs_cancel()`, path/file info operations, directory/search operations, trans/trans2, and helper callbacks such as `async_open()`, `async_simple()`, and `oplock_handler()`.

## Control Flow

Tree connect parses the requested share name, reads share options such as `cifs:server`, credentials, machine-account, S4U2Proxy, remote share, generic mapping, and trans2 mapping, then establishes an upstream SMB connection with `smb_composite_connect_send/recv()`. Operations set the upstream session PID, verify the transport is connected, translate NTVFS handles to upstream fnums, and either call synchronous `smb_raw_*` functions or, when allowed, start async raw requests and complete through callbacks that update `req->async_states`. Open creates an NTVFS handle and associates it with the upstream fnum; close removes it from the local list. Oplock breaks from upstream are translated to `ntvfs_send_oplock_break()`.

## State and Persistence Behavior

There is no local filesystem persistence. State tracks the upstream tree, transport, pending async requests, open fnum-to-NTVFS handle mappings, and configuration booleans. Disconnect destroys pending requests and backend state. File contents, metadata, locks, and notifies are persisted or managed by the upstream server.

## Dependencies and Integration Points

It depends on raw SMB client APIs, SMB composite connect, credentials/auth, Kerberos S4U2Proxy support, NTVFS operation registration, loadparm/share options, resolve context, dlink list helpers, and smbXcli connection checks. It registers as an `NTVFS_DISK` backend named `cifs`.

## Risks and Edge Cases

Close removes a file mapping before the upstream close completes, with a comment questioning whether that is ideal on failure. Many operations rely on macros mutating caller IO structures to replace NTVFS handles with fnums. `cvfs_logoff()` is a no-op because the backend cannot implement it correctly. `cvfs_copy()` and `cvfs_lpq()` are unsupported; `cvfs_trans()` is denied; `cvfs_trans2()` may be not implemented when mapping is enabled. Async cancellation only works when a matching pending request exists. Upstream disconnect marks the NTVFS request for close and returns disconnected.

## Test Signals

Tests should cover connect options for explicit credentials, machine account, delegated credentials, and S4U2Proxy; open/read/write/close handle mapping; upstream disconnect; async completion and cancellation; oplock break forwarding; notify with no timeout; generic open/read/write/lock/close mapping; unsupported copy/lpq/trans behavior; and close failure effects on local handle state.
