# sources/user-network-fs/samba/source4/torture/libnet/libnet_group.c

## Purpose
This file validates high-level libnet group APIs for create, info lookup, and paged group listing against a live SAMR/LSA-backed domain.

## Important APIs, types, and functions
`torture_groupinfo_api()` creates a temporary `libnetgrouptest` group with low-level SAMR helpers, calls `libnet_GroupInfo`, and deletes it. `torture_grouplist()` calls `libnet_GroupList` with page size 128 until completion. `torture_creategroup()` calls `libnet_CreateGroup` and cleans up through `test_group_cleanup()`. Shared helpers from `utils.c` provide domain open, group create/delete, SAMR close, and context initialization.

## Control flow
The group-info test manually opens the SAMR domain, creates a group, initializes a libnet context with SAMR/LSA pipes, requests info by group name, then deletes the group and closes the domain handle. The list test loops while `STATUS_MORE_ENTRIES` is returned, carrying `resume_index` forward and printing each group SID. The create test uses the high-level libnet API and then verifies cleanup by deleting the created group over SAMR.

## State and persistence behavior
The tests mutate the domain by creating and deleting `libnetgrouptest`. The list test is read-only but opens SAMR/LSA state in `libnet_context`. Cleanup is explicit; a failure between create and cleanup can leave the test group in the domain until a later run removes it.

## Dependencies and integration points
The file depends on `libnet/libnet.h`, generated SAMR/LSA clients, command-line credentials, loadparm workgroup settings, and helper functions declared in `torture/libnet/proto.h`. It is part of the `smbtorture` libnet suite registered elsewhere.

## Risks and edge cases
Existing stale groups are handled by helper cleanup/recreate logic, but insufficient account-management rights will fail create/delete operations. Listing treats `STATUS_MORE_ENTRIES` and `NT_STATUS_NO_MORE_ENTRIES` as expected terminal signals; regressions in resume handling would show up here.

## Test signals
The file signals that high-level libnet group wrappers can create groups, fetch group info by name, enumerate domain groups, close both SAMR and LSA handles, and clean up persistent directory objects.
