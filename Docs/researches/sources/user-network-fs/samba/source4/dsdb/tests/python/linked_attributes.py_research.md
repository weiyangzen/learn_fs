# sources/user-network-fs/samba/source4/dsdb/tests/python/linked_attributes.py

## Purpose

`linked_attributes.py` is an integration test suite for Samba AD linked-attribute behavior. It exercises ordinary group `member`/`memberOf` links, deleted and deactivated link visibility controls, duplicate handling, replace/delete semantics, one-way and DN-binary linked attributes, self-links, and backlinks that are deliberately hidden from wildcard searches. The suite validates both Windows-compatible LDAP controls and Samba-internal reveal controls.

## Important APIs, Types, and Functions

- `LATests` is the single test case class. `setUp()` opens a privileged `SamDB`, creates `CN=LATests,<domain>`, and `tearDown()` tree-deletes it unless `--no-cleanup` is set.
- `add_object()` and `add_objects()` create test users, groups, containers, `msExchConfigurationContainer`, and `msDS-KeyCredential` objects under the suite container.
- `add_linked_attribute()`, `remove_linked_attribute()`, and `replace_linked_attribute()` build `ldb.Message` instances with `FLAG_MOD_ADD`, `FLAG_MOD_DELETE`, or `FLAG_MOD_REPLACE`.
- `attr_search()`, `assert_links()`, `assert_forward_links()`, and `assert_back_links()` wrap LDAP searches with optional controls such as `show_deleted`, `show_recycled`, `show_deactivated_link`, and `reveal_internals`.
- `get_object_guid()` returns a deleted-object-safe lookup handle used by tests that inspect tombstoned objects via `<GUID=...>`.
- Command-line options control cleanup and internal visibility: `--delete-in-setup`, `--no-cleanup`, and `--no-reveal-internals`.

## Control Flow

Each test creates an isolated object graph below `CN=LATests`. Basic backlink tests add users to multiple groups and assert that forward links on groups and computed backlinks on users stay synchronized. Deletion tests remove groups or users, then compare ordinary searches with searches using deleted/recycled/deactivated-link controls. Link-modification tests verify that adding or removing linked values increments the source object's `uSNChanged` where expected, while deleting a linked target removes visible forward links without bumping the source object USN.

The suite then scales the same contract across multi-valued operations: bulk add, bulk delete, replace, all permutations of member order, relaxed-control modifications, and object creation with initial `member` values. Duplicate linked values are expected to fail with `ldb.ERR_ENTRY_ALREADY_EXISTS`.

The later tests cover schema-specific linked attributes. Real one-way `addressBookRoots` keeps a forward reference to the deleted object's new deleted DN. The "pretend one-way" `addressBookRoots2` behaves like a normal linked attribute and drops the link. `test_self_link()` verifies a group can link to itself and can still be deleted. `test_la_invisible_backlink()` checks backlink visibility rules for `msDS-KeyPrincipalBL` and `msDS-KeyCredentialLink-BL`, including wildcard `*` searches, explicit attribute requests, search filters, and DN-binary link values.

## State and Persistence Behavior

The suite mutates the live directory: it creates a temporary container, adds/removes LDAP objects, modifies linked attributes, deletes objects, and reads tombstoned entries with LDAP controls. All intended persistent changes are scoped under the test container and removed with `tree_delete:1`; PSO-like external state is not touched. If cleanup is disabled or setup cleanup is skipped after a failed run, stale `CN=LATests` objects can affect subsequent runs.

Linked attribute state is stored by the DSDB link infrastructure rather than as ordinary local Python state. Visibility varies by search controls and schema flags. Some assertions intentionally query deleted objects by GUID because their DN changes after deletion.

## Dependencies and Integration Points

The file depends on `samba.samdb.SamDB`, `ldb`, `samba.auth.system_session`, and `samba.dcerpc.misc.GUID`. It integrates with Samba's DSDB linked-attribute module, schema definitions for `member`, `memberOf`, `addressBookRoots`, `addressBookRoots2`, `msDS-KeyPrincipal`, `msDS-KeyPrincipalBL`, `msDS-KeyCredentialLink`, and `msDS-KeyCredentialLink-BL`, plus LDAP controls for deleted/recycled/deactivated links and Samba internal link reveal behavior.

## Risks and Edge Cases

- Tests use a shared fixed container name; interrupted runs need `--delete-in-setup` or manual cleanup.
- Reveal-internals tests are skipped only when `--no-reveal-internals` is passed; environments that reject Samba-only controls need that option.
- Assertions sort link values, so ordering regressions are intentionally ignored while membership-set regressions are caught.
- DN-binary links with duplicate target DNs but different binary prefixes are subtle: backlinks may contain repeated target DNs and must preserve count.
- Deleted-object assertions depend on tombstone visibility and GUID-based lookup behavior.

## Test Signals

Strong signals include duplicate-add failures, exact forward/backlink sets after add/delete/replace, `uSNChanged` changes only on source-side explicit link edits, correct behavior of `show_deactivated_link=0`, visibility differences for hidden backlinks under `*` versus explicit attributes, and successful deletion of self-linked objects.
