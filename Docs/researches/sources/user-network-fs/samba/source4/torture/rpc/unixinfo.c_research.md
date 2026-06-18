# sources/user-network-fs/samba/source4/torture/rpc/unixinfo.c

## Purpose

`unixinfo.c` is a compact torture suite for the `unixinfo` RPC interface. It tests SID to UID/GID mapping, UID/GID to SID mapping, and batched password-entry lookup by UID.

## Important APIs, Types, and Functions

The suite contains five direct test functions: `test_sidtouid()`, `test_uidtosid()`, `test_getpwuid()`, `test_sidtogid()`, and `test_gidtosid()`. It uses generated request structs `unixinfo_SidToUid`, `unixinfo_UidToSid`, `unixinfo_GetPWUid`, `unixinfo_SidToGid`, and `unixinfo_GidToSid`. `torture_rpc_unixinfo()` registers all tests against `ndr_table_unixinfo`.

## Control Flow

Each test fills one generated request, calls the corresponding `dcerpc_unixinfo_*_r()` function on the pipe binding handle, and asserts transport success. SID-to-ID tests use a synthetic BUILTIN-derived SID and accept `NT_STATUS_NONE_MAPPED` as a valid semantic result. ID-to-SID tests query UID and GID 1000 and require semantic success. `GetPWUid` builds an array of 512 UIDs from 0 to 511 and expects the batched lookup to succeed.

## State and Persistence Behavior

The suite is read-only. It does not create users, groups, or mappings. All state is request-local, allocated under the torture context, and discarded when the test context is freed.

## Dependencies and Integration Points

The file depends on `torture_rpc.h`, generated unixinfo client stubs, and SID parsing helpers from `libcli/security/security.h`. Its behavior depends on the target server's Unix identity mapping backend and NSS/passdb configuration.

## Risks and Edge Cases

UID/GID 1000 may not exist or may not map on all systems, so strict success for `UidToSid` and `GidToSid` can be environment-sensitive. The synthetic SID may or may not map, and the test correctly tolerates `NONE_MAPPED`. The 512-element `GetPWUid` request exercises bulk marshalling but assumes the server can handle that count.

## Test Signals

Passing tests indicate the unixinfo endpoint is reachable, basic SID/ID conversion paths work, and batched UID lookup marshals and returns successfully. Failures usually point to endpoint exposure, idmap configuration, NSS backend behavior, or generated NDR marshalling.
