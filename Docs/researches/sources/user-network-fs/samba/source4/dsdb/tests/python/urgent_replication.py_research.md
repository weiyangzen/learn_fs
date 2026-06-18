# sources/user-network-fs/samba/source4/dsdb/tests/python/urgent_replication.py

## Purpose

`urgent_replication.py` validates DSDB urgent replication bookkeeping. It creates, modifies, and deletes object classes and attributes whose changes should or should not advance the partition `uSNUrgent` value to match `uSNHighest`.

## Important APIs, Types, and Functions

`UrgentReplicationTests` uses `samba.tests.connect_samdb(..., global_schema=False)` to operate against a live DC. `delete_force()` deletes with `relax:0` and tolerates missing objects. The tests call `load_partition_usn()` after mutations and compare `uSNHighest` with `uSNUrgent`. They use LDB `Message`, `MessageElement`, `Dn`, and `FLAG_MOD_REPLACE` to change attributes, plus `samba.dsdb` UAC constants for urgent attribute checks.

## Control Flow

`setUp()` opens a SamDB connection and records the domain DN. Each test performs a specific mutation sequence, then checks whether the urgent USN moved. Non-urgent user object create/modify/delete should leave `uSNUrgent` behind. `nTDSDSA` and `crossRef` create/delete are urgent while ordinary modify is not. `attributeSchema` and `classSchema` changes are urgent. `secret` and `rIDManager` create/modify are urgent but delete is not. User `userAccountControl`, `lockoutTime`, and `pwdLastSet` modifications are urgent, while `description` and deletion are not.

## State and Persistence Behavior

The test writes real objects under domain, configuration, schema, and system naming contexts. Several creates use `relax:0` to bypass normal restrictions for schema or configuration objects. Random OID suffixes reduce collisions for schema test objects, but cleanup is incomplete for some schema cases because deleted schema definitions are not simply removed. The central persistent signal is partition metadata: `load_partition_usn()` exposes whether the urgent replication marker was updated by the preceding transaction.

## Dependencies and Integration Points

The file integrates with DSDB replication metadata, schema handling, urgent replication trigger logic, and the LDB module stack. It depends on the domain, configuration, and schema naming contexts being writable by the test credentials and on Samba's `load_partition_usn()` helper returning both `uSNHighest` and `uSNUrgent`.

## Risks and Edge Cases

Schema tests can be environment-sensitive: `classSchema` creation is caught and skipped if the add fails, but the modify branch still assumes the object exists. Random OIDs can still collide in long-running or reused environments. The tests compare equality immediately after a mutation, so unrelated concurrent writes to the same partition can make `uSNHighest` advance and produce false negatives.

## Test Signals

Passing tests show that Samba marks urgent replication exactly for AD-sensitive classes and attributes. Regressions surface as equality mismatches between `uSNHighest` and `uSNUrgent`, or as unexpected LDB errors while adding schema/configuration objects.
