# sources/user-network-fs/samba/source4/torture/drs/python/repl_secdesc.py

## Purpose
`repl_secdesc.py` verifies security descriptor inheritance across DRS replication. It focuses on inherited ACE propagation for new objects, existing objects, renamed objects, moved subtrees, and conflict-renamed children.

## Important APIs, Types, And Functions
- `ReplAclTestCase` extends `drs_base.DrsBaseTestCase`.
- `sd_utils.SDUtils` is used to add ACEs and read SDDL from both DCs.
- The important SDDL fragments are `mod` (`(A;CIOI;GA;;;SY)`), `mod_becomes` (`(A;OICIIO;GA;;;SY)`), and `mod_inherits_as` (`(A;OICIIOID;GA;;;SY)`).
- Tests rely on `_disable_all_repl()`, `_net_drs_replicate()`, and `_enable_all_repl()` to control replication points.

## Control Flow
`setUp()` creates a parent OU, initializes SD helpers for both DCs, disables replication, and synchronizes both DCs. Individual tests add inheritable ACEs either before or after child creation and before or after replication. Rename tests create OUs outside the protected parent, replicate them, add parent ACEs, move them under the parent, then force replication and compare SDDL. The conflict test creates a same-name child on DC2, applies inherited ACLs and a rename on DC1, replicates to trigger conflict handling, then replicates back.

## State And Persistence Behavior
The test mutates OU trees and their `nTSecurityDescriptor` values. The parent test OU is deleted with `tree_delete:1` during teardown. Replication is disabled during test setup and restored afterward. The important persistent state under assertion is the normalized SDDL on DC1 and DC2 after DRS applies inherited ACEs.

## Dependencies And Integration Points
This file integrates with Samba ACL/security descriptor helpers, LDB object creation and rename operations, and DRS replication metadata handling. It tests the DSDB/repl metadata path that recalculates inherited security descriptors when parent ACLs arrive, objects are moved, or conflict DNs are produced.

## Risks
The function names contain the misspelling `inheirt`, which is harmless but affects test discovery names. The tests assume SDDL normalization is stable and identical between DCs. Conflict tests depend on replication winner behavior and may be sensitive to object versioning and ordering. Cleanup must remove nested OUs or later tests may see inherited ACL residue.

## Test Signals
Expected signals include parent SDDL containing `mod_becomes`, child SDDL containing `mod_inherits_as`, byte-for-byte SDDL equality between DC1 and DC2, `ERR_NO_SUCH_OBJECT` before expected replication, and inherited ACLs preserved after subtree moves and conflict resolution.
