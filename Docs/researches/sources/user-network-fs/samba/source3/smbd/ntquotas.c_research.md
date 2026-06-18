# sources/user-network-fs/samba/source3/smbd/ntquotas.c

## Purpose
This file adapts Unix/VFS disk quota data to Samba's NT quota structures. It retrieves and sets per-user quotas through the VFS layer, converts quota units and sentinel values, enumerates user quota entries, and allocates quota-list handles.

## Important APIs, Types, and Functions
`limit_nt2unix()` maps NT byte limits to Unix quota blocks while preserving Samba sentinel values. `limit_unix2nt()` maps Unix block counts to NT byte counts. `vfs_get_ntquota()` resolves an optional SID to uid, obtains a real cwd pathref fsp, calls `SMB_VFS_GET_QUOTA()`, and fills `SMB_NTQUOTA_STRUCT`. `vfs_set_ntquota()` converts an NT quota into `SMB_DISK_QUOTA` and calls `SMB_VFS_SET_QUOTA()`. `vfs_get_user_ntquota_list()` enumerates passwd users and builds an `SMB_NTQUOTA_LIST`. `init_quota_handle()` allocates an `SMB_NTQUOTA_HANDLE` with a destructor that frees the quota list.

## Control Flow
Get operations validate `fsp`, connection, and output pointers, zero output, convert SID to uid when supplied, open a real pathref for the connection cwd because quota VFS calls need a real fsp, call the VFS quota method, restore errno after freeing the pathref, and populate NT fields. Set operations initialize disk quota fields with `QUOTABLOCK_SIZE`, translate soft/hard limits, optionally resolve SID to uid, and delegate to the VFS. Enumeration calls `setpwent()`, loops over passwd entries, skips duplicate uids, converts uid to SID, calls `vfs_get_ntquota()`, skips empty quota entries, allocates list nodes under one talloc context, and appends them.

## State and Persistence
The file itself stores no global state. Quota state lives in the filesystem/VFS backend. The user quota list is talloc-owned; each node records the shared memory context so `free_ntquota_list()` can release it through the handle destructor.

## Dependencies and Integration Points
It depends on smbd file/connection structures, VFS quota operations, SID/uid mapping, passwd enumeration, and Samba quota structs/constants. It integrates with SMB quota query/set handling elsewhere in smbd and with backend filesystem quota modules through `SMB_VFS_GET_QUOTA` and `SMB_VFS_SET_QUOTA`.

## Risks and Edge Cases
`limit_unix2nt()` multiplies without overflow checks. `limit_nt2unix()` rounds sub-block positive limits up to one block and maps `SMB_NTQUOTAS_NO_ENTRY` to no limit. `vfs_set_ntquota()` logs SID conversion failure but still calls the VFS with uid -1, which depends on backend interpretation. Enumerating all passwd users can be expensive or incomplete in directory-service environments. Empty quota detection treats both soft and hard zero as no entry.

## Test Signals
No direct tests are in this group. Useful tests would cover sentinel conversions, sub-block rounding, SID lookup failure, VFS errno mapping, passwd duplicate uid handling, empty quota skipping, and handle destructor cleanup. Integration tests need a quota-capable VFS/backend.
