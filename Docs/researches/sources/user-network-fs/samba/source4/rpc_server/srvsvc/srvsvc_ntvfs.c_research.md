# sources/user-network-fs/samba/source4/rpc_server/srvsvc/srvsvc_ntvfs.c

## Purpose

This file provides the SRVSVC helper that creates a temporary NTVFS connection to a named share so SRVSVC file security operations can query or set path security descriptors through the same backend mechanisms used by SMB file access.

## Important APIs, Types, And Functions

`struct srvsvc_ntvfs_ctx` wraps an `ntvfs_context *` so talloc cleanup can disconnect it. `srvsvc_ntvfs_ctx_destructor()` calls `ntvfs_disconnect()`. `srvsvc_create_ntvfs_context()` is the exported helper: it obtains the caller session, messaging context, server ID, share context/config, derives the NTVFS type from the share type, initializes an NTVFS connection with `ntvfs_init_connection()`, sets local/remote addresses, creates a request, performs `ntvfs_connect()`, and returns the connected NTVFS context.

## Control Flow

The helper looks up the share through `share_get_context()` and `share_get_config()`. It maps `SHARE_TYPE` to `NTVFS_IPC`, `NTVFS_PRINT`, or `NTVFS_DISK`, allocates the wrapper, initializes the NTVFS connection with protocol `PROTOCOL_NT1`, registers the destructor, sets addresses from the DCE/RPC connection, creates an `ntvfs_request` with the caller's auth session and call timestamp, then invokes the NTVFS tree-connect hook with the share name. On success, callers receive `c->ntvfs`.

## State And Persistence

The NTVFS context is per-call/per-allocation runtime state. It is talloc-owned by the supplied memory context and disconnects through the destructor. This file does not persist configuration or file data; persistence occurs only when callers use the returned context for NTVFS operations such as ACL updates.

## Dependencies And Integration Points

The file integrates SRVSVC with Samba share configuration, DCE/RPC session/address helpers, imessaging, server IDs, NTVFS connection/request APIs, raw tree-connect structures, loadparm context, and the helper prototype consumed by `dcesrv_srvsvc.c`.

## Risks And Edge Cases

The share-type mapping is fragile: the `else if (sharetype && strcmp(sharetype, "PRINTER"))` condition treats any non-`PRINTER` non-`IPC` value as print because `strcmp()` is nonzero, leaving actual `PRINTER` shares to fall through as disk. That appears inverted from the intended check and can misclassify disk shares. Host allow/deny checks are disabled behind `#if 0`. The context uses a hardcoded `PROTOCOL_NT1` and PID 0. Errors during init leave partial allocations to talloc cleanup, but callers must not retain the returned pointer beyond its memory context.

## Test Signals

Test signals include SRVSVC file security get/set on disk, IPC, and printer shares, verification that NTVFS disconnect runs on talloc free, share-not-found errors, address propagation checks in backends that inspect client/server addresses, and a targeted regression test for the share-type branch so `DISK`, `PRINTER`, and `IPC` map to the intended `NTVFS_*` enum values.
