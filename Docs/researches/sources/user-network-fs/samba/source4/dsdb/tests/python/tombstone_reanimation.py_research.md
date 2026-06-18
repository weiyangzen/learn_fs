# sources/user-network-fs/samba/source4/dsdb/tests/python/tombstone_reanimation.py

## Purpose

`tombstone_reanimation.py` validates Samba AD deleted-object restoration. It covers basic undelete operations, forbidden rename paths, restoration with attribute modifications, same-NC versus cross-NC constraints, and detailed attribute plus replication metadata expectations for users, password-bearing users, groups, OUs, and containers.

## Important APIs, Types, and Functions

`RestoredObjectAttributesBaseTestCase` connects with `samba.tests.connect_samdb_env()`, captures domain, schema, and configuration DNs, and calls `PasswordCommon.allow_password_changes()` so password tests can set user passwords. It provides `search_guid()` using `<GUID=...>` with `show_deleted:1`, `search_dn()` using `show_recycled:1`, `_create_object()`, attribute comparison helpers, `_check_metadata()`, and the static `restore_deleted_object()` helper.

`restore_deleted_object()` performs reanimation by modifying the deleted object DN with `show_deleted:1`, deleting `isDeleted`, replacing `distinguishedName`, and optionally replacing additional attributes. The metadata checks unpack `drsblobs.replPropertyMetaDataBlob` and compare ordered `(attid, version)` pairs using many `DRSUAPI_ATTID_*` constants.

## Control Flow

Basic restore tests create users or containers, capture GUIDs, delete objects, locate deleted objects by GUID, then restore by LDAP modify. Negative cases assert `ERR_NO_SUCH_OBJECT` without `show_deleted`, `ERR_UNWILLING_TO_PERFORM` for renaming a deleted object, `ERR_ENTRY_ALREADY_EXISTS` when the target DN is occupied, and `ERR_OPERATIONS_ERROR` when trying to restore across naming contexts.

The object-specific classes define expected attribute dictionaries and metadata arrays. `RestoreUserObjectTestCase` validates initial add state, deleted/recycled state, and restored state for a user without password. `RestoreUserPwdObjectTestCase` does the same with password and supplemental credential metadata, restoring with a replacement `userPassword`. Group tests ensure plain groups restore with expected defaults and that deleted group membership is not restored. Container tests ensure OUs and containers restore expected naming/category attributes while excluding attributes Windows does not restore, such as OU `description` and container `showInAdvancedViewOnly`.

## State and Persistence Behavior

The suite creates and deletes live AD objects and intentionally searches deleted/recycled objects. Restored objects retain original GUIDs and SIDs where expected. The recycle-bin enable helper exists but is not called by the visible tests; nevertheless tests expect `isRecycled` on deleted objects, so the target environment must support the relevant deletion behavior. Password tests modify password-related replicated attributes and permit password changes during setup.

## Dependencies and Integration Points

This file integrates with Samba's delete-object path, Deleted Objects container, recycled object visibility controls, LDAP modify semantics for reanimation, password handling, schema formatting for GUIDs, DRS replication metadata encoding, and Windows-compatible attribute stripping/restoration rules. It uses `ldb` error constants to verify exact failure modes.

## Risks and Edge Cases

The metadata assertions are intentionally strict about attid ordering and version numbers, with `None` used only where version variance is tolerated. Changes in replication metadata ordering, default attributes, password policy side effects, or Windows compatibility choices can break tests even if high-level restore works. Some local variables such as `orig_attrs` and `del_attrs` are computed but not used in a few tests, indicating historical comparison logic was simplified. Fixed object names can collide after interrupted runs, although many paths call `delete_force()` before creation.

## Test Signals

Pass signals include deleted objects being restorable by modify but not by rename, target-DN collisions and cross-NC restores failing with exact LDB errors, restored users retaining GUID/SID and expected account defaults, password-user metadata showing password-related version increments, groups restoring without `member`, OUs/containers restoring with expected `lastKnownParent`, and replication metadata matching the expected add/delete/restore transitions.
