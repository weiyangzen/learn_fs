# sources/user-network-fs/samba/source4/torture/rpc/fsrvp.c

## Purpose
This file defines the `rpc.fsrvp` suite for the File Server Remote VSS Protocol. It validates path support, version/context negotiation, shadow-copy set creation, expose/delete flows, timeout behavior, snapshot SMB I/O, previous-version enumeration, bad IDs, abort behavior, and share security-descriptor cloning.

## Important APIs, Types, And Functions
`torture_rpc_fsrvp()` binds to `ndr_table_FileServerVssAgent`. The central helper `test_fsrvp_sc_create()` sequences `IsPathSupported`, `GetSupportedVersion`, `SetContext`, `StartShadowCopySet`, `AddToShadowCopySet`, `PrepareShadowCopySet`, `CommitShadowCopySet`, `ExposeShadowCopySet`, and `GetShareMapping`, with injected timeout checkpoints from `enum test_fsrvp_inject`. `test_fsrvp_sc_delete()` calls `DeleteShareMapping`. Other tests use SMB2 helpers, `FSCTL_SRV_ENUM_SNAPS`, SRVSVC `NetShareGetInfo/SetInfo`, and security descriptor APIs.

## Control Flow
Basic tests call individual RPCs or create/delete one shadow-copy mapping. Share-I/O tests connect to `fsrvp_share`, write `pre-snap`, create a snapshot, overwrite the base file with `post-snap`, connect to the snapshot share, and confirm the snapshot still reads `pre-snap`. Enumeration tests create one or two snapshots and query snap counts through SMB2 IOCTL. Share-SD testing reads the base share DACL, adds one placeholder ACE before snapshot creation, stops before expose, adds another ACE, exposes the snapshot, restores the original base DACL, and checks the snapshot DACL.

## State And Persistence Behavior
The suite requires a snapshotable share named `fsrvp_share` and creates shadow-copy sets, exposed snapshot shares, files named `testfss.dat`, and temporary DACL modifications. Most created mappings are deleted, but `test_fsrvp_enum_created()` intentionally frees mappings without deletion so enumeration can observe snapshots. Timeout injection may leave incomplete server-side shadow-copy state depending on server cleanup. Share-SD test restores the base share DACL before checking the snapshot.

## Dependencies And Integration Points
Dependencies span generated FSRVP and SRVSVC RPC stubs, SMB2 client APIs, SMB command-line credentials, name resolution, security descriptors/SIDs, HRESULT mapping, and Samba loadparm settings such as `fss:sequence timeout`. The comments document Windows Server requirements for NDR64, signing, domain membership, and an FSRVP-capable share.

## Risks And Edge Cases
The tests are operationally heavy and can leave snapshots, exposed shares, modified ACLs, or test files on failures. Timeout tests sleep for configured sequence timeouts plus a margin, so they can be slow. Enumeration expectations note Windows Server 2012 behavior may not list FSRVP-created snapshots as previous versions. Placeholder ACEs cause the share-SD test to skip if those built-in operator SIDs already exist.

## Test Signals
Signals include zero FSRVP HRESULTs for normal sequences, exact FSRVP/HRESULT errors after injected timeout or bad IDs, snapshot share mapping GUID equality, SMB2 data equality for pre-snapshot content, expected previous-version counts, successful DACL restoration, and both placeholder ACEs appearing in the snapshot share DACL at expose time.
