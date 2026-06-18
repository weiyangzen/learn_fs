<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_full_audit.c -->
# sources/user-network-fs/samba/source3/modules/test_vfs_full_audit.c

## Purpose
This cmocka unit test verifies the operation-name table used by the `vfs_full_audit` module. It is a small compile-and-runtime guard that every VFS operation index has a non-null audit name and that the recorded operation type matches the array index.

## Important APIs, Types, And Functions
The file declares `vfs_full_audit_init` for static builds, includes `vfs_full_audit.c` directly, and checks `vfs_op_names`. `test_full_audit_array` iterates from zero to `SMB_VFS_OP_LAST - 1`, asserting `vfs_op_names[i].name != NULL` and `vfs_op_names[i].type == i`.

## Control Flow
`main` builds a one-test cmocka array, enables subunit output, and runs without custom setup or teardown. The included module provides the audit operation metadata under test.

## State And Persistence
No durable state is touched. The test only reads static data compiled from `vfs_full_audit.c`.

## Dependencies And Integration Points
It depends on Samba includes, `smbd/smbd.h`, cmocka, and the full-audit VFS implementation. It integrates with the build as a regression test for keeping VFS operation enum ordering synchronized with audit metadata.

## Risks
The test only validates table completeness and enum alignment, not audit logging behavior, syslog formatting, configuration parsing, or success/failure filtering. Direct inclusion of the implementation can expose static-build or dependency drift.

## Test Signals
A passing run shows that newly added or reordered `SMB_VFS_OP_*` values have matching `vfs_op_names` entries. Failures usually indicate a missing audit operation name or an enum/table ordering bug.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_full_audit.c -->
