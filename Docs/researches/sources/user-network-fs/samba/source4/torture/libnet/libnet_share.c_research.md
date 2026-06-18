# sources/user-network-fs/samba/source4/torture/libnet/libnet_share.c

## Purpose
`libnet_share.c` exercises libnet SRVSVC share listing and share deletion, with a direct RPC helper used to create a temporary share before deletion.

## Important APIs, types, and functions
`test_displayshares()` prints `libnet_ListShares` results for SRVSVC info levels 0, 1, 2, 501, and 502. `torture_listshares()` calls `libnet_ListShares` for each level. `test_addshare()` directly calls `dcerpc_srvsvc_NetShareAdd_r` with a `srvsvc_NetShareInfo2`. `torture_delshare()` then calls `libnet_DelShare` for `libnetsharetest`.

## Control flow
The list test resolves the target host from the torture RPC binding, creates a libnet context, and loops through supported enumeration levels. The deletion test connects to SRVSVC, creates a disk-tree share pointing at `C:\WINDOWS\TEMP`, then requests deletion through libnet.

## State and persistence behavior
Listing is read-only. The delete test persists a temporary server share and removes it, so failure after `NetShareAdd` can leave `libnetsharetest` registered on the server. The test assumes a Windows-like path and administrative share-management privileges.

## Dependencies and integration points
The file depends on generated SRVSVC clients, libnet share APIs, command-line credentials, and `torture_rpc_connection()`. It integrates with server service semantics rather than SAMR/LSA domain state.

## Risks and edge cases
`test_addshare()` only checks transport NTSTATUS, not the embedded SRVSVC result field, so share-add semantic failures may be underreported. The hard-coded `C:\WINDOWS\TEMP` path is Windows-centric and may not map on Samba servers without suitable configuration.

## Test signals
The list test confirms each share info level can be fetched and decoded. The delete test confirms libnet can remove a share created by raw SRVSVC calls.
