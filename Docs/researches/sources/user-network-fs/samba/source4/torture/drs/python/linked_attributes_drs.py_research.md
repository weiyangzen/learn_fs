# sources/user-network-fs/samba/source4/torture/drs/python/linked_attributes_drs.py

## Purpose

`linked_attributes_drs.py` is a small DRS test module for forward linked-attribute visibility through `DsGetNCChanges`. It verifies that deleting a group, deleting individual membership links, or deleting a linked target user produces the expected active and inactive linked-attribute records in raw DRS output.

## Important APIs, Types, and Functions

`LATests` derives from `drs_base.DrsBaseTestCase`. `setUp()` selects DC1 as `samdb`, creates `OU=la,<domain>`, records the DC invocation id, and binds to DRS. `tearDown()` deletes the OU tree and ignores missing-object cleanup errors.

Object helpers are `add_object()`, `add_objects()`, `add_linked_attribute()`, `remove_linked_attribute()`, and `get_object_guid()`. `delete_user()` removes a user from a local `self.users` list, but that list is not initialized or used by the shown tests, making this helper effectively stale.

The central helper is `attr_search()`. It builds a `DRSUAPI_EXOP_REPL_OBJ` request with `_exop_req8()`, calls `self.drs.DsGetNCChanges()`, selects linked attributes matching `DRSUAPI_ATTID_<attr>`, unpacks each link value blob as `DsReplicaObjectIdentifier3`, and returns `(dn, active)` pairs based on `DRSUAPI_DS_LINKED_ATTRIBUTE_FLAG_ACTIVE`. `assert_forward_links()` compares these pairs to an expected mapping of DN to active boolean.

## Control Flow and Scenarios

`test_links_all_delete_group()` creates two users and two groups, adds memberships, deletes one group, asserts the surviving group still replicates its active member link, then searches the deleted group with `show_deleted:1` by GUID and asserts it has no forward links.

`test_la_links_delete_link()` creates two groups and two users, removes and re-adds membership links, and repeatedly asserts that raw DRS returns both active and inactive link records for the group as links are toggled. It validates inactive records after deletion and active records after re-add.

`test_la_links_delete_user()` deletes a target user after group memberships exist and asserts raw DRS for the source groups no longer returns links to the deleted user, while unrelated active links remain.

## State and Persistence Behavior

All state is stored under a single test OU on DC1 and cleaned by tree delete. The tests do not involve DC2 replication; they inspect the local DC's DRS representation after LDAP changes. Deleted groups are found by GUID with `show_deleted:1`, and raw link state is observed through DRS rather than LDAP search results.

## Dependencies and Integration Points

Dependencies include `sys.path.insert(0, "bin/python")`, `ldb`, `samba.dcerpc.drsuapi`, `samba.dcerpc.misc`, `samba.ndr.ndr_unpack`, `samba.ndr.ndr_pack` (imported but unused), and `drs_base`. The main integration point is direct `DsGetNCChanges` `EXOP_REPL_OBJ` on DC1, plus LDAP add/modify/delete operations.

## Risks and Edge Cases

This file is compact but depends on raw DRS link ordering only indirectly by set-style assertions. `attr_search()` ignores its `expected` and `scope` parameters, which are harmless but misleading. The unused `LATestException`, `delete_user()`, and `ndr_pack` import are stale signals. Since only DC1 is used, the file tests DRS exposure of local linked attributes, not inter-DC convergence.

## Test Signals

Signals are exact count matches from `assert_forward_links()`, active-flag comparisons for each expected DN, GUID-based lookup of deleted objects, and DRS unpacking of linked-attribute target identifiers rather than LDAP-only membership checks.
