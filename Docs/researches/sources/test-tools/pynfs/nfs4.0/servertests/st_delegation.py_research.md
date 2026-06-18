# sources/test-tools/pynfs/nfs4.0/servertests/st_delegation.py

## Purpose
`st_delegation.py` tests NFSv4 read and write delegation behavior, callback recall handling, callback-server errors, delegation return, lease renewal under callback path failure, share interactions, callback-server changes, CLAIM_DELEGATE_CUR, recall triggers from namespace operations, server-side external mutations, and self-conflict cases.

## Important APIs, Types, And Functions
- `_handle_error` retries failed `DELEGRETURN` callback handling asynchronously.
- `_recall(c, thisop, cbid)` is a callback handler that sends `PUTFH` plus `DELEGRETURN` for `CB_RECALL`.
- `_cause_recall(t, env)` uses `env.c2` to open a conflicting writer, retrying on `NFS4ERR_DELAY`.
- `_verify_cb_occurred(t, c, count)` checks callback recall count and validates stored recall response.
- `_get_deleg(...)` creates or opens a file with callback recall configured and returns delegation info, filehandle, and stateid, warning if the expected delegation type is not granted.
- `_read_deleg` and `_write_deleg` parameterize read/write delegation recall scenarios.
- `testReadDeleg*`, `testWriteDeleg*`, `testCloseDeleg`, `testManyReaddeleg`, `testRenew`, `testIgnoreDeleg`, `testDelegShare`, `testChangeDeleg`, `testClaimCur`, `testRemove`, `testLink`, `testRename`, `testRenameOver`, `testServer*`, and self-conflict tests cover the scenario matrix.

## Control Flow
Tests initialize a client with a callback server (`init_connection(..., cb_ident=0)`), request a delegation through create/open helpers with `set_recall=True`, then create conflicts using a second client, namespace operations, or `env.serverhelper`. Callback handling is synchronized by a module-level `threading.Lock` because the callback thread and tester thread share the client's packer/unpacker. Many loops accept `NFS4ERR_DELAY`, sleep, and retry until the conflicting operation completes or an expected denial occurs.

`testChangeDeleg` creates a new `CBServer`, swaps the callback endpoint with SETCLIENTID/CONFIRM, and then verifies recalls arrive on the new server. Server-side tests call `serverhelper` to run operations such as unlink, rename, link, and chmod outside the NFS client. CLAIM_DELEGATE_CUR tests use a recalled delegation stateid to perform delegated opens before returning the delegation.

## State And Persistence Behavior
The module creates files and open/delegation state on the server, manipulates callback server state (`opcounts`, stored recall results, `c.cbid`), and may invoke external server-side mutations. It relies on lease time, callback paths, delegation stateids, and open/share state persisting across multiple clients and threads during each test.

## Dependencies And Integration Points
It imports NFS constants/types, `check`, `os`, `threading`, `time`, `nfs_ops`, and dynamically imports `nfs4lib.CBServer` in one test. It depends on `NFS4Client` callback-server support, `env.c1`/`env.c2`, `env.serverhelper`, and server delegation support.

## Risks And Edge Cases
- The local `nfs4server.py` returns no delegations and `DELEGRETURN`/`DELEGPURGE` are not supported, so these tests primarily apply to real NFS servers.
- `_handle_error.run` references `ops` instead of `self.ops`, a likely bug in the retry path.
- Threading is timing-sensitive; sleeps are used to let callback paths settle.
- Many tests use `t.word()` repeatedly to build paths; correctness depends on stable per-test word behavior.
- Callback and security behavior can vary significantly across servers, producing warnings for unsupported delegation instead of hard failures.

## Test Signals
Signals include receiving `OPEN_DELEGATE_READ` or `OPEN_DELEGATE_WRITE`, `OP_CB_RECALL` count increments, successful `DELEGRETURN`, expected callback error handling, `NFS4ERR_DELAY` retry behavior, `NFS4ERR_SHARE_DENIED` for deny-write cases, callback path down behavior on RENEW, and no unnecessary recall for same-client/self-conflict scenarios.
