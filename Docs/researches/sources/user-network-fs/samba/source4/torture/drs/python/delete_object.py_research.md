# sources/user-network-fs/samba/source4/torture/drs/python/delete_object.py Research

## Purpose
This module tests how deleted objects and linked attributes replicate between two DCs when concurrent modifications occur on one DC and deletion occurs on another. It verifies tombstone shape, deletion replication ordering, and group membership backlink cleanup.

## Important APIs, Types, And Functions
`DrsDeleteObjectTestCase` derives from `DrsBaseTestCase`. `setUp()` disables inbound and outbound replication on both DCs, then forces synchronization both ways. `tearDown()` re-enables replication. `_check_obj()` searches by original `objectGUID` with `show_deleted:1`, locates the Deleted Objects container, and verifies either normal object state or deleted-object state, including `isDeleted`, stripped attributes, DN location, and `name/cn` mangling with `DEL:<guid>`.

## Control Flow
`test_ReplicateDeletedObject1()` creates a user on DC1, replicates it to DC2, deletes it on DC1, modifies the live copy on DC2 with a description and group membership, then tests both replication directions to ensure the deletion wins and does not resurrect the object. It also deletes related groups and verifies backlink cleanup. `test_ReplicateDeletedObject2()` creates the same conflict but sends the deletion to DC2 before pulling DC2 back to DC1, validating the alternate ordering.

## State And Persistence
The tests alter DC replication options, create users and groups, modify links, delete objects, and force replication. They rely on teardown to re-enable replication. Deleted objects remain as tombstones by design. Failures can leave replication disabled or temporary objects present.

## Dependencies And Integration Points
The module depends on LDB, `drs_base` helpers, two writable DCs, `samba-tool drs options`, and `samba-tool drs replicate`. It combines direct LDAP writes with explicit replication commands.

## Risks And Test Signals
Signals are correct tombstone attributes, Deleted Objects DN placement, unchanged deleted state after conflicting modification replication, and removal of forward links. Risks include cleanup failure for replication options, timing-sensitive replication state, leftover tombstones, and incomplete TODO coverage for `replPropertyMetaData` and recycle-bin behavior.
