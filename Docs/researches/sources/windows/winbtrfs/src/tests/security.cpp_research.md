# File Research: sources/windows/winbtrfs/src/tests/security.cpp

## Purpose

`security.cpp` tests Windows security descriptor behavior on WinBtrfs: access-mask reporting, DACL/SACL/label storage, owner and group operations, privilege-gated security changes, inherited ACE behavior, mandatory integrity labels, traverse checks, and denied security queries/updates.

## Main Helpers

- `create_file_sd(...)`: wraps `NtCreateFile` with an explicit security descriptor.
- `create_file_with_acl(...)`: creates a security descriptor with one `ACCESS_ALLOWED_ACE` for Everyone.
- `set_dacl(...)`: sets a DACL on an existing handle.
- `get_acl(...)`: queries DACL, SACL, or label ACLs and validates returned self-relative security descriptor layout.
- `sid_to_string(...)` and `compare_sid(...)`: SID formatting and comparison helpers.
- `set_owner(...)`, `get_owner(...)`, `set_group(...)`, `get_group(...)`: owner/group operations.
- `set_audit(...)`: writes a system audit ACE.
- `set_mandatory_access(...)`: writes a mandatory label ACE.
- `duplicate_token(...)`, `adjust_token_level(...)`, `set_thread_token(...)`: token setup for impersonation/integrity tests.

## Behavior Covered

The first section checks `FILE_ACCESS_INFORMATION` for handles opened with `GENERIC_READ`, `GENERIC_WRITE`, and `GENERIC_EXECUTE`, asserting exact expanded access masks.

DACL coverage creates and modifies ACLs containing Everyone ACEs, then re-queries and validates ACE type, flags, mask, and SID bytes. It includes maximum access masks and explicitly empty or restricted DACLs.

Owner and group tests show privilege boundaries. Setting an arbitrary owner fails without `SeRestorePrivilege`, while setting group succeeds in the tested path. After enabling `SeRestorePrivilege`, setting/querying owner succeeds.

SACL coverage validates `ACCESS_SYSTEM_SECURITY` failure without `SeSecurityPrivilege`, then enables the privilege, opens the file, writes an audit ACE, and verifies that SACL persists after privilege changes.

Mandatory integrity label coverage writes a high-integrity `SYSTEM_MANDATORY_LABEL_NO_WRITE_UP` label, then impersonates a duplicated medium-integrity token. The test confirms write access is denied and `MAXIMUM_ALLOWED` excludes write access while still allowing read/delete-related rights.

Creation-time security descriptor tests create a file with an explicit DACL and verify that the handle’s granted access remains the requested `READ_CONTROL`, while the stored DACL grants `FILE_READ_DATA` to Everyone. Creating a file with another user as owner is expected to fail with `STATUS_INVALID_OWNER`.

Inheritance coverage creates directories with `OBJECT_INHERIT_ACE` and `OBJECT_INHERIT_ACE | CONTAINER_INHERIT_ACE`, then verifies inherited ACE flags on child files and directories, including `INHERIT_ONLY_ACE` behavior for container inheritance.

Traverse behavior is explicitly tested. A directory missing `FILE_TRAVERSE` denies child creation. Adding `FILE_TRAVERSE` allows it. Removing `FILE_TRAVERSE` again still allows child creation after enabling `SeChangeNotifyPrivilege`, documenting the bypass-traverse-checking privilege.

The final section opens a file with only `FILE_READ_ATTRIBUTES` and verifies that owner, group, DACL, SACL, label queries and all corresponding set operations fail with `STATUS_ACCESS_DENIED`.

## Integration Points

This file uses shared harness primitives `create_file`, `query_information`, `exp_status`, `adjust_token_privileges`, and `disable_token_privileges`. It also exports `set_dacl`, which is reused by rename tests for destination permission scenarios.

## Research Notes

`security.cpp` is both a security descriptor serialization test and an access-check compatibility test. It is important for any WinBtrfs code touching Windows ACL persistence, owner/group translation, privilege checks, integrity labels, or inherited ACE propagation.
