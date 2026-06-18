# sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_session.py

## Purpose
`st_destroy_session.py` tests `DESTROY_SESSION` lifecycle behavior, connection binding, callback recovery after session destruction, compound placement rules, and a skeleton for lock conflict races.

## Important APIs, Types, and Functions
- `testDestroyBasic` checks that operations using a destroyed session fail and a new session works.
- `testDestroy` verifies connection binding before destroying from a new TCP connection.
- `testDestroy2` and `testDestroy3` verify callback behavior after session destruction and recreation.
- `testDestoryNotFinalOps` and `testDestoryNotSoleOps` check RFC placement rules.
- `testDestroyLockConfRace` is present but incomplete.

## Control Flow
Tests create sessions, destroy them through raw or session compounds, then attempt further operations. Callback tests obtain delegations, trigger recalls from a second client, destroy the callback-bearing session, create a new session, and wait for callback delivery.

## State and Persistence Behavior
The tests manipulate session tables, connection binding state, callback channels, delegation state, and open state. They expect destroyed sessions to become invalid while client records can create replacement sessions.

## Dependencies and Integration Points
The module depends on environment helpers, generated open types, `nfs_ops`, threading events, and `rpc.rpc` connection helpers.

## Risks and Edge Cases
Two function names spell `Destroy` as `Destory`, but that only affects test names. Callback retry timing uses long waits and depends on server callback policy. `testDestroyLockConfRace` is incomplete and should not be treated as a full assertion.

## Test Signals
Expected statuses include `NFS4ERR_BADSESSION` after destruction, `NFS4ERR_CONN_NOT_BOUND_TO_SESSION` before binding a new connection, `NFS4_OK` after proper binding, callback arrival events, and `NFS4ERR_NOT_ONLY_OP` for illegal compound placement.
