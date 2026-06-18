# sources/user-network-fs/samba/source4/dsdb/tests/python/deletetest.py

Purpose: this deletion correctness suite verifies AD delete protection, tree-delete behavior, tombstone attributes, RDN mangling, preserved attributes, parent GUIDs, and deleted-object container placement for domain and configuration objects.

Important APIs/types/functions: `BaseDeleteTests` provides `GUID_string()`, `search_guid()`, and `search_dn()` using `show_deleted:1`. `BasicDeleteTests` checks delete protection and helper assertions `del_attr_values()`, `preserved_attributes_list()`, `check_rdn()`, and `delete_deleted()`. `BasicTreeDeleteTests.setUp()` creates users, a group with members, a site subtree, captures live objects and deleted-container GUIDs, then `test_all()` and `test_tree_delete()` perform deletion variants and call `check_all()`.

Control flow: after host parsing and `SamDB` setup, `test_delete_protection()` creates a non-leaf container and verifies plain delete fails while tree delete succeeds; it then checks protected DC, RID set, crossRef, Users, and Computers objects reject deletion as expected. Tree tests create fresh timestamped objects, delete them individually or via tree delete, then repeatedly search by GUID and validate tombstone metadata.

State and persistence behavior: test fixtures are persistent AD objects. Timestamped names reduce collisions, and `delete_force()` clears prior objects during setup. Deleted objects remain in deleted-object containers or under deleted parents as tombstones; this is intentional and inspected.

Dependencies and integration points: depends on Samba `SamDB`, LDB error constants, tree-delete and show-deleted controls, DSDB well-known deleted-object container GUIDs, and `schema_format_value` for objectGUID strings.

Risks: this test is destructive in the target domain/config partitions and should not run against production directories. It assumes specific AD protection rules and deleted-object placement. The repeated large assertions duplicate checks, making maintenance noisy but explicit.

Test signals: expected LDB errors (`ERR_NOT_ALLOWED_ON_NON_LEAF`, `ERR_UNWILLING_TO_PERFORM`, `ERR_NO_SUCH_OBJECT`), `isDeleted=TRUE`, absence of stripped attributes, preserved metadata, `name`/RDN `DEL:<GUID>` formatting, parent GUIDs, and rejected deletion of already-deleted DNs.
