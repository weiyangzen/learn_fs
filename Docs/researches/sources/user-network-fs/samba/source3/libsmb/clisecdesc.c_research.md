# sources/user-network-fs/samba/source3/libsmb/clisecdesc.c

## Purpose

This file implements querying and setting security descriptors on open files through SMB1 NT transact security descriptor operations or SMB2 query/set-info security operations.

## Important APIs, Types, and Functions

Public APIs are `cli_query_security_descriptor_send/recv`, `cli_query_security_descriptor()`, `cli_query_secdesc()`, `cli_query_mxac()`, `cli_set_security_descriptor_send/recv`, `cli_set_security_descriptor()`, and `cli_set_secdesc()`. Query and set state structs store SMB1 parameter buffers and marshalled/unmarshalled descriptor blobs.

## Control Flow

Query send selects SMB2 `cli_smb2_query_info_fnum_send()` with `SMB2_0_INFO_SECURITY` or SMB1 `NT_TRANSACT_QUERY_SECURITY_DESC` with fnum and `sec_info` in an 8-byte parameter block. Query recv unmarshals the returned descriptor when the caller asks for it. Set send first marshals the descriptor, then dispatches to SMB2 set-info security or SMB1 `NT_TRANSACT_SET_SECURITY_DESC`. `cli_set_secdesc()` derives `SECINFO_*` bits from descriptor content and present flags.

## State and Persistence Behavior

Queries are read-only. Set operations persist remote owner, group, DACL, or SACL state depending on `sec_info`. Local state is request-scoped and talloc-owned; recv calls mark requests received where appropriate.

## Dependencies and Integration Points

The file integrates with `marshall_sec_desc()`, `unmarshall_sec_desc()`, SMB2 fnum helpers, `cli_trans`, and security descriptor constants. `cli_query_mxac()` is SMB2-only and delegates to `cli_smb2_query_mxac()`.

## Risks and Test Signals

Risks include incorrect `sec_info` selection, large descriptors near the 0x10000 SMB1 output size, malformed descriptor unmarshalling, SACL privilege failures, and dialect differences. Tests should cover owner/group/DACL/SACL combinations, null output descriptor queries, malformed returned blobs, SMB1 and SMB2 set/query round trips, MXAC unsupported on SMB1, and sync wrapper rejection with active async calls.
