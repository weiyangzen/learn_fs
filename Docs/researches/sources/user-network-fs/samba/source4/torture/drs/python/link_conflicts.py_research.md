# sources/user-network-fs/samba/source4/torture/drs/python/link_conflicts.py

## Purpose

`link_conflicts.py` tests Samba DRS conflict resolution for linked attributes when two DCs independently create, delete, or update conflicting link state. It focuses on single-valued links such as `managedBy`, multi-valued links such as `member`, generated backlinks such as `memberOf`, active versus deleted link state, object-deletion precedence, full-sync behavior, and link metadata versioning.

## Important APIs, Types, and Functions

The test class is `DrsReplicaLinkConflictTestCase`, derived from `drs_base.DrsBaseTestCase`. `setUp()` creates a stable test OU on DC1, binds DRS connections to both DCs, and disables inbound replication on both DCs so every conflict scenario can control exactly when bidirectional replication runs. `tearDown()` re-enables inbound replication, deletes the test OU tree, and delegates to the base teardown.

Constants `DC1_TO_DC2` and `DC2_TO_DC1` select replication order. `sync_DCs()` performs a two-step manual sync in the requested order so each test can make either DC resolve the conflict first. `ensure_unique_timestamp()` sleeps one second to force timestamp ordering when tests need deterministic "newer" metadata.

Object and link helpers are `get_guid()`, `add_object()`, `modify_object()`, `add_link_attr()`, `del_link_attr()`, and `unique_dn()`. `assert_attrs_match()` verifies expected attribute value counts on both DCs and checks value equality. `zero_highwatermark()` returns a zeroed `DsReplicaHighWaterMark` for full `REPL_OBJ` reads. `_check_replicated_links()` uses `_check_replication()` against both DCs with `DRSUAPI_EXOP_REPL_OBJ` and `AbstractLink` expectations to confirm raw DRS still preserves active and inactive conflict links that LDAP cannot show directly.

## Control Flow and Scenarios

Each conflict test creates source and target objects, syncs to establish a common baseline, applies divergent updates on the two DCs, calls `sync_DCs()` in both possible orders through a wrapper public test, and checks convergence.

Single-valued link tests cover different `managedBy` targets on two DCs, duplicate same-target additions, conflicts where the winning or losing link has been deleted, and reactivating link values that already exist as inactive metadata. Multi-valued tests cover same-DN conflicting user objects in a group membership, duplicate membership additions, and backlink repair when conflicting source groups are renamed with `CNF` names.

Deletion tests verify that a link delete versus active link conflict resolves by metadata version, that deleting a source or target object trumps a concurrent link add, and that doing full-sync cycles before a conflict does not change link conflict semantics. `test_link_attr_version()` directly calls `_get_replication()` for a single object and asserts the first linked-attribute metadata version is `1`.

## State and Persistence Behavior

State is stored in the real DC databases and isolated under the test OU. Inbound replication is disabled for the lifetime of each test case, so divergent object/link states persist on each DC until explicit sync calls. The tests rely on GUID-based searches to follow objects after conflict renames and use DRS raw link checks to observe inactive/deleted link records that are not visible through ordinary LDAP attributes.

Random suffixes in `unique_dn()` avoid collisions because some public test methods execute the same helper twice with different sync orders. Timestamp sleeps provide deterministic ordering for conflict algorithms that consider originating time. Version-sensitive tests create add/delete/add sequences to prove version number can beat timestamp recency.

## Dependencies and Integration Points

Dependencies include `drs_base`, `samba.tests`, `ldb`, `random`, `time`, `drs_base.AbstractLink`, `samba.dcerpc.drsuapi`, and `samba.dcerpc.misc`. Integration is with Samba LDAP operations, DRS bind handles to both DCs, `net drs replicate`, `DsGetNCChanges` via `_check_replication()`, and linked-attribute attids such as `DRSUAPI_ATTID_managedBy`.

## Risks and Edge Cases

The tests are intentionally sensitive to replication order, metadata timestamps, and metadata version increments. A one-second sleep is coarse but necessary for timestamp-based conflict resolution; slow or unusual environments can still make timing assumptions expensive. Because inbound replication is disabled in setup, teardown must reliably re-enable it to avoid contaminating later tests.

Conflict expectations are subtle: active links generally beat deleted alternatives in single-valued conflict cases, but version can beat timestamp in deletion conflicts. Raw DRS link verification is essential because LDAP cannot expose deleted link metadata; regressions that only affect inactive-link replication would be missed by LDAP-only assertions.

## Test Signals

Primary signals are cross-DC convergence checks for exact attribute counts and values, explicit checks for `CNF:<guid>` conflict-renamed objects, absence of `member`/`memberOf` after object-deletion conflicts, raw `AbstractLink` expected active/inactive records from DRS, and the linked-attribute version assertion.
