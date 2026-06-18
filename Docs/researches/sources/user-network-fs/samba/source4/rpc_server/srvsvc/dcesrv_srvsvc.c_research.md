# sources/user-network-fs/samba/source4/rpc_server/srvsvc/dcesrv_srvsvc.c

## Purpose

This file implements the server side of Samba's SRVSVC DCE/RPC interface. It exposes Windows-compatible server service operations for share enumeration, share get/set/add/delete, share name validation, server metadata, remote time, disk enumeration, and file security operations, while returning explicit faults or not-supported errors for many legacy character-device, session, file, transport, path, and DFS opnums.

## Important APIs, Types, And Functions

`SRVSVC_CHECK_ADMIN_ACCESS` enforces that sensitive share info levels are visible only to builtin administrators or server operators. `dcesrv_srvsvc_NetShareAdd()` converts level 2 and 502 share info into Samba `share_info` arrays and calls `share_create()`. `dcesrv_srvsvc_fiel_ShareInfo()` fills SRVSVC share info unions for levels 0, 1, 2, 501, 502, and 1005 from `share_config`. `dcesrv_srvsvc_NetShareEnumAll()` and `dcesrv_srvsvc_NetShareEnum()` enumerate configured shares; the latter hides shares marked with `STYPE_HIDDEN`. `dcesrv_srvsvc_NetShareGetInfo()` fetches one share, and `dcesrv_srvsvc_NetShareSetInfo()` uses `dcesrv_srvsvc_fill_share_info()` plus `share_set()` to update configurable fields.

Other implemented operations include `NetShareCheck`, `NetSrvGetInfo`, `NetDiskEnum`, `NetTransportEnum` stubs with allocated empty arrays, `NetRemoteTOD`, `NetNameValidate`, `NetGetFileSecurity`, `NetSetFileSecurity`, and `NetShareDel`. Many other opnums call `DCESRV_FAULT(DCERPC_FAULT_OP_RNG_ERROR)` or return `WERR_NOT_SUPPORTED` after constructing empty containers for compatibility.

## Control Flow

Most operations switch on the incoming info level, allocate the matching generated NDR container, fill it, and return `WERR_INVALID_LEVEL` for unknown levels. Share creation and setting build arrays of generic `share_info` name/type/value records, normalize Windows `C:\path` style paths by dropping the drive prefix and converting backslashes to slashes, then call the share backend. Share enumeration obtains a `share_context`, lists share names, fetches each config, fills the requested info structure, and updates `totalentries`.

Server metadata flow reads `lpcfg_dcerpc_server_info()` and common helpers for platform, server name, server type, and server string. `NetRemoteTOD` snapshots system time and fills Windows remote time fields. `NetNameValidate` validates share names only for name type 9 and enforces the normal vs 8.3-style length limits. File security calls create an NTVFS context for the named share, construct raw path-info or setpath-info requests, and delegate ACL get/set to `ntvfs_qpathinfo()` or `ntvfs_setpathinfo()`.

## State And Persistence

Share add/set/delete persist through Samba's share backend reached by `share_create()`, `share_set()`, and `share_remove()`. Server info, disk info, transport arrays, and time responses are computed from configuration or current process state and are not persisted by this file. File security operations persist ACL changes through the underlying NTVFS backend and filesystem. The code owns only per-call talloc allocations for NDR response structures.

## Dependencies And Integration Points

The file integrates with generated `ndr_srvsvc` server dispatch, Samba DCE/RPC call/session state, share backend APIs, `rpc_server/common/share.h` helpers, loadparm server metadata, security token helpers, NTVFS raw file info/setfileinfo operations, time helpers, and generated `ndr_srvsvc_s.c`. It relies on `srvsvc_create_ntvfs_context()` from `srvsvc_ntvfs.c` for file security access.

## Risks And Edge Cases

Administrative access checks are present for some sensitive info levels but TODO comments remain for several share get/set/add paths, so authorization relies partly on backend enforcement. Path normalization assumes Windows drive-prefixed paths and does not fully validate filesystem reachability. Share security descriptors are marked TODO for add/set levels 502, so descriptor persistence may be incomplete. Enumeration has TODO paging support and can fail if a share disappears after name enumeration. A likely share-type bug exists in `srvsvc_ntvfs.c` rather than here, but it affects file security calls from this file. Many opnums intentionally fault, which can surprise clients expecting partial legacy support.

## Test Signals

Useful tests include SRVSVC RPC enumeration at levels 0, 1, 2, 501, and 502; admin vs non-admin access to protected levels; add/get/set/delete share round trips including path normalization; hidden share behavior difference between `NetShareEnum` and `NetShareEnumAll`; share name validation edge cases; server info levels 100-102; remote time and disk enum smoke tests; file security get/set over disk shares; and client compatibility tests for unsupported/faulting legacy calls.
