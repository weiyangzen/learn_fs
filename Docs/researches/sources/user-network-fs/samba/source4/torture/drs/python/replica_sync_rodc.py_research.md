# sources/user-network-fs/samba/source4/torture/drs/python/replica_sync_rodc.py

## Purpose
`replica_sync_rodc.py` tests negative conflict behavior for single-object local replication into an RODC. It ensures Samba refuses replication cases where accepting a single object or rename would leave the RODC high-watermark inconsistent with an unresolved local DN conflict.

## Important APIs, Types, And Functions
- `DrsReplicaSyncTestCase` extends `drs_base.DrsBaseTestCase`.
- `_create_ou()` creates an OU in the domain NC and returns a string GUID through `get_string()`.
- `_check_deleted()` mirrors the writable-DC helper but expects string `TRUE` values.
- Tests use `_net_drs_replicate()` with `local=True`, `single=True`, and `forced=True`.

## Control Flow
Setup disables replication on DC1 and assumes DC2 is the RODC from the environment. Each test first fully replicates from DC1 to the RODC. `test_ReplConflictsRODC()` creates an object, single-replicates it to the RODC, deletes it on DC1 without replicating that deletion, creates a new same-DN object, and expects the next single-object replication to fail. `test_ReplConflictsRODCRename()` follows the same shape but collides by renaming a second object into the first object's DN after the RODC already has the old object.

## State And Persistence Behavior
The file mutates domain OUs on DC1 and relies on the RODC retaining a prior view. It deliberately avoids replicating delete state before introducing the conflict. It restores replication on DC1 in teardown but does not maintain a large cleanup framework because the success path is failure of replication, with cleanup attempts in exception paths.

## Dependencies And Integration Points
This integrates DRS local/single replication with RODC behavior. It depends on the test environment providing `DC2` as an RODC, Samba's GUID binding syntax, and base replication helpers. The integration point under test is protection against advancing replication state when a single-object update cannot safely resolve an RODC-side DN conflict.

## Risks
The tests intentionally expect exceptions and treat a non-exception as failure. Broad `except` blocks mean the exact failure code is not asserted, only that replication fails. If environment `DC2` is not an RODC, the semantics may not hold. Cleanup is less comprehensive than in `replica_sync.py`, so failures can leave test objects behind.

## Test Signals
The expected signal is failure of the final single-object local replication. A successful final replication is a hard test failure because it would imply the RODC accepted an update that could incorrectly advance the high-watermark.
