# sources/test-tools/pynfs/nfs4.1/server41tests/st_delegation.py

## Purpose
`st_delegation.py` tests NFSv4.1 open delegations, recall callbacks, callback security parameters, delegation revocation, delegation conflict rules, CB_GETATTR, and reads using delegation stateids after close.

## Important APIs, Types, and Functions
- `_got_deleg`, `__create_file_with_deleg`, and `_create_file_with_deleg` obtain and validate delegations.
- `_testDeleg` sets callback hooks, triggers a conflicting open from another client, waits for `CB_RECALL`, returns the delegation, and checks the waiting open.
- `_testCbGetattr` installs `CB_GETATTR` response hooks and compares attributes seen by another client.
- Tests cover read/write/any/no delegation, callback auth flavors, `BACKCHANNEL_CTL`, revocation with `TEST_STATEID`/`FREE_STATEID`, self-conflict behavior, write-open vs read delegation, `CB_GETATTR`, and delegation read after close.

## Control Flow
Most tests create a first session with callback hooks, obtain a delegation through OPEN/create, then create a second session to issue a conflicting OPEN or GETATTR. The first session responds to recall or getattr callbacks, and the test checks the second request outcome.

## State and Persistence Behavior
The tests rely on delegation stateids surviving close in valid cases, revocation state being reflected in SEQUENCE status flags, callback channels carrying recall/getattr, and server state clearing after `FREE_STATEID`.

## Dependencies and Integration Points
The module depends on environment helpers, `st_open.open_claim4`, generated NFS types/constants, `nfs_ops`, `nfs4lib`, and callback-hook support in the client harness.

## Risks and Edge Cases
Delegation support varies by server and export. Tests use short waits for callbacks and can be timing-sensitive. Some expectations, such as `OPEN_DELEGATE_NONE_EXT` for no-delegation requests, require modern protocol support. The file has duplicated imports and minor typos in comments, but functional intent is clear.

## Test Signals
Expected signals include `NFS4_OK` for valid delegation operations, callback arrival events for `OP_CB_RECALL` and `OP_CB_GETATTR`, `NFS4ERR_DELAY` as an acceptable conflict response, `NFS4ERR_DELEG_REVOKED`, `SEQ4_STATUS_RECALLABLE_STATE_REVOKED`, and correct callback credential flavors.
