# sources/user-network-fs/samba/source4/torture/drs/python/repl_move.py

## Purpose

`repl_move.py` is a large Samba DRS integration test module for object moves, renames, deletes, and conflict resolution across two DCs. It validates that users and OUs keep correct DNs, names, parent GUIDs, deletion state, and replication metadata when moved between containers, renamed in place, modified concurrently on another DC, deleted, replicated in different directions, or created under conflicting parent containers.

## Important APIs, Types, and Functions

`DrsMoveObjectTestCase` derives from `drs_base.DrsBaseTestCase`. `setUp()` disables replication on both DCs, force-syncs them, creates a top test OU plus two sibling OUs (`DrsOU1`, `DrsOU2`) on DC1, replicates them to DC2, records both invocation IDs, and binds DRS connections to both DCs. `tearDown()` deletes the top OU, re-enables replication on both DCs, and delegates to the base teardown.

`_make_username()` creates timestamped user names. `_check_obj()` is the main object-state assertion helper: it searches by original object GUID with `show_deleted:1`, compares RDN, `name`, DN, `parentGUID`, and `isDeleted` behavior for live versus deleted objects, and optionally calls `_check_metadata()`. `_check_metadata()` unpacks LDAP `replPropertyMetaData` as `drsblobs.replPropertyMetaDataBlob` and optionally performs a raw DRS `DRSUAPI_EXOP_REPL_OBJ` request to compare DRS metadata and attribute attids against expected tuples of `(attid, originating_invocation_id, version)`.

`DrsMoveBetweenTreeOfObjectTestCase` tests deeper OU trees. Its `setUp()` creates DN objects and dictionaries for nested OUs (`DrsOU1`, `DrsOU2`, `DrsOU2B`, `DrsOU2C`, `DrsOU3` through `DrsOU6`) and disables replication. Its `_check_obj()` is a smaller GUID-based checker for CN/name/DN/deleted state and parent placement.

The file imports many DRSUAPI attid constants for metadata tables: user attributes, name/CN/OU attributes, deletion attributes such as `isDeleted`, `isRecycled`, `lastKnownParent`, and DRS request types such as `DsGetNCChangesRequest8`, `DsReplicaHighWaterMark`, and `DsReplicaObjectIdentifier`.

## Control Flow and Scenarios

`test_ReplicateMoveObject1` through `test_ReplicateMoveObject11` cover user and OU movement between two sibling OUs, rename-only moves, concurrent description modifications on DC2, deletion on DC1 or DC2, replication in DC1-to-DC2 and DC2-to-DC1 directions, and cases where the peer had never seen the moved object. Early tests include detailed metadata expectation tables for initial creation, move, delete, and concurrent description states; later tests focus on behavioral object checks and description preservation/removal.

The common flow is: create or locate a user/OU on DC1, optionally replicate to DC2, rename/move it on DC1, optionally modify `description` on DC2 at the old DN, run manual replication in a chosen direction, assert the live object is at the expected DN with expected metadata and description, delete it, replicate cleanup, and assert deleted-object semantics and metadata.

`DrsMoveBetweenTreeOfObjectTestCase` expands this into deep tree and parent-conflict cases. It verifies moving a user into a newly created nested OU chain, moving users back, moving parent OUs around after users have been moved, shuffling sibling OUs through temporary names, combining unrelated attribute modifications with rename operations to force out-of-USN-order replication, adding users under OUs whose parent metadata sorts after the child, and resolving conflicting parent OUs by timestamp/version so the child lands under the intended `parentGUID`.

## State and Persistence Behavior

The tests deliberately disable automatic replication and use forced `_net_drs_replicate()` calls as the only propagation mechanism. This makes the database state on DC1 and DC2 intentionally divergent during each scenario. Objects are followed by GUID, not DN, because moves, conflict renames, and deletion mangling change DNs.

Persistent assertions inspect both ordinary LDAP attributes and replication metadata. Deleted objects are searched with `show_deleted:1`; deleted DNs and names are expected to preserve the pre-delete RDN prefix before deletion mangling, and live objects must preserve exact DN/name/RDN equality plus `parentGUID`. Description attributes modified on the losing side are expected either to survive on live objects or disappear after deletion conflict resolution, depending on the scenario.

Metadata tables encode originating DC and version behavior. Notably, RDN attributes are skipped in raw DRS metadata comparisons because the RDN itself is not sent as an ordinary DRS attribute in the same way as LDAP `replPropertyMetaData`.

## Dependencies and Integration Points

Dependencies include `time`, `samba.tests`, `samba.ndr.ndr_unpack`, `samba.dcerpc.drsblobs`, `samba.dcerpc.misc`, `samba.drs_utils.drs_DsBind` (imported but not used directly), `ldb`, `drs_base`, and many `samba.dcerpc.drsuapi` constants and request classes. The integration points are Samba LDAP `newuser`, add, rename, modify, delete, GUID search, raw DRS `DsGetNCChanges` `EXOP_REPL_OBJ`, `replPropertyMetaData`, and manual forced DRS replication.

## Risks and Edge Cases

This is a brittle but valuable integration suite. It depends on exact metadata ordering, exact attid sequences, invocation IDs, version increments, and deletion mangling behavior. Repeated large metadata tables make maintenance error-prone; changing Samba's metadata representation can require updating many expected lists. Timestamp-derived usernames can collide if multiple tests create the same value within one second in a shared OU, although each test creates its own top OU.

Replication must be re-enabled in teardown even after failures. The tests also rely on modifying objects at old DNs on DC2 while DC1 has renamed them, which is intentional but sensitive to whether the peer has already seen prior changes. Deep-tree tests rely on `parentGUID` rather than DN strings to disambiguate conflicting parent containers.

## Test Signals

Signals include GUID-based live/deleted object lookup, exact DN/RDN/name/parentGUID assertions, absence or presence of `description`, exact `isDeleted` expectations, LDAP `replPropertyMetaData` attid/origin/version matching, raw DRS `REPL_OBJ` metadata checks, successful forced replication in both directions, and final parentGUID equality after complex tree shuffles and conflict resolution.
