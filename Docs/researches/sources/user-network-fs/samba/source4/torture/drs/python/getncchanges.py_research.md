# sources/user-network-fs/samba/source4/torture/drs/python/getncchanges.py

## Purpose

`getncchanges.py` is an integration test module for Samba Active Directory DRS `DsGetNCChanges` behavior. It constructs two-domain-controller replication scenarios and validates that paged replication, highwatermark handling, ancestor fetching, linked-attribute target fetching, deleted-object handling, cross-partition links, and naming-context root ordering do not lose objects or links.

The tests are not general library code. They are executable torture/subunit tests that drive real Samba DCs named by `DC1` and `DC2`, using `drs_base.DrsBaseTestCase` helpers for DRS binds, replication calls, highwatermark retrieval, GUID extraction, link extraction, and manual `net drs replicate` operations.

## Important APIs, Types, and Functions

The main class is `DrsReplicaSyncIntegrityTestCase`, derived from `drs_base.DrsBaseTestCase`. `setUp()` creates a per-test OU on DC2, points test LDAP state at DC2, records the base DN, and installs a `DcConnection` wrapper for the default DC. `init_test_state()` resets received DNs, links, GUIDs, the last DRS counter, `max_objects`, and booleans tracking whether GET_ANC and GET_TGT were actually used.

Core helpers include `add_object()`, `modify_object()`, and `delete_attribute()` for LDAP setup; `create_object_range()` for deterministic numbered OU trees; `assert_expected_data()` and `assert_expected_links()` for final coverage assertions; `assert_object_has_link()` for comparing replicated link GUID blobs against `extended_dn` LDAP results; `restore_deleted_object()` for clearing `isDeleted` and replacing `distinguishedName`; and `sync_DCs()` for explicit replication.

The central DRS client helpers are `_repl_send_request()` and `repl_get_next()`. `_repl_send_request()` reuses the previous response's `new_highwatermark` and `uptodateness_vector`, sets `DRSUAPI_DRS_WRIT_REP`, optionally sets `DRSUAPI_DRS_GET_ANC`, and optionally sends `DRSUAPI_DRS_GET_TGT` as a `more_flags` value. `repl_get_next()` calls `_get_replication()`, extracts DNs, GUIDs, and links from the returned ctr6, and recursively retries the same page with GET_ANC or GET_TGT when it sees an unknown parent, source GUID, or target GUID.

`DcConnection` stores a bound DRS connection, handle, default highwatermark, uptodateness vector, `ldb` connection, and DNS name for switching between DCs. `set_dc_connection()` copies that state back onto the inherited `DrsBaseTestCase` fields.

`DrsReplicaSyncFakeAzureAdTests` inherits the full integrity suite but overrides `modify_highwatermark()` to zero `reserved_usn`, modeling Azure AD / Entra ID Connect behavior. It skips most parent tests via `SKIPPED_TESTS`, leaving only cases expected to be meaningful under zeroed reserved USN.

## Control Flow and Scenarios

Most test methods follow a pattern: create ordered objects and optional linked attributes, start a paged replication cycle, mutate objects or links in the middle of the cycle, continue calling `repl_get_next()` until `replication_complete()` returns true, then assert that every expected object and link was received.

`test_repl_integrity()` validates that modifying objects while a paged cycle is in progress does not drop objects. `test_repl_integrity_get_anc()` creates parent/child ordering where children can appear before parents, forcing GET_ANC. `test_repl_get_tgt()` and `test_repl_get_tgt_chain()` force GET_TGT by sending links before their targets are known, including a long B/C chain reachable from A objects.

Linked-attribute scenarios cover adding links during replication, parents with linked attributes under GET_ANC, combined GET_TGT and GET_ANC with nested targets, deleted link source/target objects, reanimated objects, cross-partition links into the Configuration NC, cross-partition deleted targets, and multi-valued links that may arrive in link-only chunks.

Lower-level request validation covers invalid NC/GUID combinations, full replication with `DummyDN` and valid GUID, interleaving `EXOP_REPL_OBJ` with full replication pages, and ensuring full replication pages do not overlap. The NC-root tests in `_test_repl_nc_is_first()` verify that the naming context root is first under full or NC-change cases and that `tmp_highest_usn` and `highest_usn` advance in expected ways.

## State and Persistence Behavior

Test state is deliberately local to a test case but mutates real Samba LDAP databases. Objects are created under a test OU and removed via cleanup with `tree_delete:1`. The class tracks received DNs, object GUID strings, linked attributes, `last_ctr`, GET_ANC/GET_TGT usage, and connection-specific highwatermarks.

DRS continuation state persists through `last_ctr.new_highwatermark` and `last_ctr.uptodateness_vector`. `start_new_repl_cycle()` preserves the last counter enough to continue from the previous highwatermark while clearing link state and flag tracking for a second cycle. Several tests disable replication on DC2, perform batches of local changes, and then re-enable/sync so the peer receives a controlled replication stream.

Deleted objects are inspected or restored using `show_deleted:1`, GUID-based LDAP binds, `isDeleted`, and `distinguishedName` replacement. Cross-partition tests create temporary server objects under the Configuration partition and explicitly replicate `nc_dn=self.config_dn`.

## Dependencies and Integration Points

The module depends on `drs_base`, `samba.tests`, `ldb`, `samba.dcerpc.drsuapi`, `samba.dcerpc.misc`, `samba.WERRORError`, and `samba.werror`. It assumes the Samba DRS torture environment exports DC names and credentials and that `drs_base.DrsBaseTestCase` provides DC LDAP handles, DNS names, config DN, DRS bind helpers, replication helpers, GUID formatting, ctr6 object/link extraction, and replication enable/disable hooks.

Integration points are the DRSUAPI `DsGetNCChanges` operation, Samba LDAP modify/delete/add operations, `net drs replicate` via `_net_drs_replicate()`, and the replication metadata/link representation returned by `drs_base` helper methods.

## Risks and Edge Cases

The tests are timing and ordering sensitive because they rely on USN ordering, object creation order, and mid-cycle mutations. Some behavior differs between Samba and Windows, and comments explicitly note optional Microsoft behavior, Windows duplicate ancestor sends, and Samba-specific ordering. The recursive retry behavior in `repl_get_next()` can hide a broken test setup if object/link ordering does not force the expected flag, so tests assert `used_get_anc` or `used_get_tgt` where relevant.

Large object counts and real DC replication make the suite slow. Cross-partition and reanimation scenarios are high-risk because incomplete cleanup or failed re-enable paths can leave DCs in unusual states; the tests use explicit cleanup and re-enable calls but still depend on a healthy integration environment.

## Test Signals

Strong signals include exact object coverage via `assert_expected_data()`, link-count and GUID-blob validation via `assert_expected_links()`, GET_ANC/GET_TGT flag usage assertions, DRS error-code checks such as `WERR_DS_DRA_BAD_NC`, highwatermark monotonicity assertions, link-only chunk detection, and consistency checks against both primary and secondary DCs using `assert_DCs_replication_is_consistent()`.
