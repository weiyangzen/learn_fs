# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dump.c

## Purpose

`nfs_dump.c` implements panic-time crash dump writes to an NFS swap/dump file. It sends NFS WRITE RPCs directly over a connectionless transport with minimal dependencies because normal kernel services, context switching, and timeout behavior are constrained after a panic.

It supports NFSv2 and NFSv3 dump targets.

## Main Interfaces

Primary entry point:

- `nfs_dump`

Internal helpers:

- `nd_init`
- `nd_send_data`
- `nd_get_reply`
- `nd_poll`
- `nd_auth_marshall`
- `nd_log`

Static dump state includes:

- `nfsdump_cf`
- `nfsdump_addr`
- `nfsdump_fhandle2`
- `nfsdump_fhandle3`
- `nfsdump_maxcount`
- `nfsdump_version`

## Dump Flow

`nfs_dump()` initializes the transport state through `nd_init()`, then writes one page at a time. For each page, it sends an NFS WRITE request with `nd_send_data()`, polls for a reply with `nd_poll()`, and decodes/validates replies with `nd_get_reply()`.

Retries are controlled by `RETRIES` and a timeout that grows with the retry count. Bad or unrelated messages are ignored and polling continues until the matching reply arrives or retry limits are exceeded.

## Initialization

`nd_init()` lazily fills static dump state from the dump vnode if not already initialized:

- NFS protocol version from `mi_vers`
- v2 or v3 filehandle from the vnode
- maximum dump file size from `dumpvp_size`
- server netbuf and netconfig from current server info

If the original transport is not connectionless, `nd_init()` attempts to convert INET/INET6 TCP-style config to UDP/UDP6 by constructing a clone device. Non-INET non-connectionless transports fail with `EIO`.

It then opens the transport with `t_kopen()` and binds a reserved port for INET/INET6, or performs a generic `t_kbind()` otherwise.

## WRITE RPC Encoding

`nd_send_data()` creates an RPC call header, allocates a one-page dump buffer, and attaches two mblks:

- a fixed header buffer containing the XDR-encoded RPC/NFS WRITE arguments
- a continuation mblk containing the page data copied from the dump source address

For NFSv2 it encodes `RFS_WRITE`, the filehandle, begin offset, offset, length, and byte-array length.

For NFSv3 it encodes `NFSPROC3_WRITE`, the NFSv3 filehandle, 64-bit offset, count, `FILE_SYNC` stable mode, and byte-array length.

It refuses to extend the dump file beyond `nfsdump_maxcount` and trims the final write if it would cross the file size.

## Reply Handling

`nd_get_reply()` receives UDP data with `t_krcvudata()`, tolerates `EBADMSG` as a bad message, validates that the message type is `T_DATA`, initializes XDR over the received mblk, and decodes the RPC reply.

The accepted-reply result decoder depends on NFS version:

- NFSv2 uses `xdr_attrstat`
- NFSv3 uses `xdr_WRITE3res`

The function checks the reply XID against the call XID, converts RPC-level errors with `_seterr_reply()`, and verifies the NFS status is success. It frees any auth verifier returned by the server and frees the received mblk after successful decode.

## Polling

`nd_poll()` uses `t_kspoll()` in a loop until data is available or the timeout expires. It briefly lowers interrupt priority with `spl0()`/`splx()` before checking the transport because the network transports do not support true polled I/O here. It calls `runqueues()` inside the wait loop.

If the maximum retry count is reached without an event, it reports that the server is not responding and returns `EIO`.

## Authentication

`nd_auth_marshall()` writes AUTH_UNIX credentials directly into the XDR stream using `XDR_INLINE()`. It uses:

- current high-resolution time seconds
- `utsname.nodename`
- uid 0
- gid 0
- empty group list
- AUTH_NULL verifier

This is a minimal panic-time credential path, not the normal RPC auth stack.

## Notable Invariants

- Dump writes are page-sized except for trimming at dump file EOF.
- NFSv3 writes are sent as `FILE_SYNC`.
- The dump code does not extend a swap-backed dump file.
- Only NFSv2 and NFSv3 are supported.
- The code tries to force dumping over UDP-style connectionless transport.
- Reply XIDs must match the sent call XID; unrelated replies are ignored.
- The path is designed for panic context and avoids normal blocking abstractions where possible.

## Dependencies

This file depends on:

- NFS filehandle and mntinfo/rnode structures
- Kernel TLI APIs: `t_kopen`, `t_kbind`, `t_ksndudata`, `t_krcvudata`, `t_kspoll`
- RPC/XDR routines: `xdr_callhdr`, `xdr_replymsg`, `xdr_fhandle`, `xdr_nfs_fh3`, `xdr_WRITE3res`
- STREAMS mblk APIs
- Dump globals such as `dumpvp_size`
- Network config and address state from the NFS mount

## Research Notes

The key risk areas are panic-context allocation failures, mblk lifetime on send or encode errors, transport conversion to UDP/UDP6, retry behavior around bad or unrelated replies, and correctness of file-size trimming. This code is intentionally narrow and bypasses most normal NFS client machinery.
