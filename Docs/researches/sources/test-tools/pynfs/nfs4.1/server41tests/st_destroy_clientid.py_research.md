# sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_clientid.py

## Purpose
`st_destroy_clientid.py` tests `DESTROY_CLIENTID` behavior for unconfirmed clients, nonexistent clientids, clients with sessions, compound placement, and repeated destroy calls.

## Important APIs, Types, and Functions
- Tests include `testSupported`, `testDestroyCIDWS`, `testDestroyBadCIDWS`, `testDestroyBadCIDIS`, `testDestroyCIDSessionB`, `testDestroyCIDCSession`, `testDestroyCIDNotOnly`, and `testDestroyCIDTwice`.

## Control Flow
Tests create clients and sometimes sessions, then send `op.destroy_clientid(clientid)` either outside a session through `env.c1.compound` or inside a session through `sess.compound`. They assert the status for each lifecycle case.

## State and Persistence Behavior
The file exercises client records before and after confirmation, session association, and removal from the server's clientid table. Repeated calls validate stale-clientid behavior after removal.

## Dependencies and Integration Points
It depends on `st_create_session.create_session`, environment assertions, `nfs_ops`, and `nfs4lib`.

## Risks and Edge Cases
The embedded `nfs4server.py` in this group does not implement `op_destroy_clientid`, so these tests target compliant external servers or code not shown here. The use of clientid `0` as nonexistent is a heuristic and can collide in artificial servers.

## Test Signals
Expected statuses are `NFS4_OK`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_CLIENTID_BUSY`, and `NFS4ERR_NOT_ONLY_OP`.
