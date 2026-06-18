# sources/user-network-fs/samba/source4/torture/libnet/groupinfo.c

## Purpose

`groupinfo.c` tests `libnet_rpc_groupinfo()` by creating a temporary SAMR group, querying it by SID and by group name, and cleaning it up.

## Important APIs, Types, and Functions

- `TEST_GROUPNAME` is `libnetgroupinfotest`.
- `test_groupinfo()` builds a group SID from the domain SID and RID, then queries level 5 by SID and by name.
- `torture_groupinfo()` connects to SAMR, opens the domain, creates the test group, runs the groupinfo checks, and deletes the group.
- Shared helpers `test_domain_open()`, `test_group_create()`, and `test_group_cleanup()` come from other libnet torture support.

## Control Flow

After a SAMR RPC connection, the test opens the configured workgroup domain, creates the temporary group and captures its RID, calls `libnet_rpc_groupinfo()` with the SID string, resets the request, calls it again with `groupname`, then cleans up the group and frees memory.

## State and Persistence Behavior

The test creates and deletes a SAMR group. If it fails before cleanup, the group named `libnetgroupinfotest` may remain in the domain.

## Dependencies and Integration Points

It depends on SAMR RPC, libnet groupinfo API, domain SID manipulation (`dom_sid_add_rid`, `dom_sid_string`), loadparm workgroup, and shared group test helpers. It is registered as `net.groupinfo`.

## Risks and Edge Cases

Cleanup is skipped if earlier setup fails before reaching the cleanup call. Level 5 is hard-coded and noted as needing extension. Existing groups with the same name can collide with the test.

## Test Signals

Passing requires domain open, group create, groupinfo by SID, groupinfo by name, and cleanup all to return `NT_STATUS_OK` or true from helpers.
