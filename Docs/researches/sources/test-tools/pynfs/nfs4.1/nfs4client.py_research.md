# sources/test-tools/pynfs/nfs4.1/nfs4client.py

## Purpose
`nfs4client.py` implements the pynfs NFSv4.1/4.2 client and callback server used by tests. It can issue raw COMPOUND calls, establish client IDs and sessions, manage foreground/backchannel sequence slots, handle callback COMPOUND requests, install callback hooks, and assist state-protection/SSV tests.

## Important APIs, Types, And Functions
- `NFS4Client(rpc.Client, rpc.Server)` connects to an NFS server, exposes NFSv4 RPC client methods, and registers as an NFS callback server.
- `compound_async`, `compound`, `listen`, `null_async`, `null`, `control_async`, and `control` are the primary RPC call helpers.
- Callback handlers `handle_0`, `handle_1`, `op_cb_compound`, `op_cb_sequence`, `op_cb_getattr`, `op_cb_recall`, `op_cb_notify_lock`, and `op_cb_layoutrecall` process server-to-client callbacks.
- `new_client`, `new_client_session`, and `new_pnfs_client_session` wrap `EXCHANGE_ID`, `CREATE_SESSION`, and `RECLAIM_COMPLETE`.
- `ClientStateProtection` builds SSV crypto context data from `EXCHANGE_ID` state-protection results.
- `ClientRecord` stores clientid, sequence id, flags, credentials, SSV handles, and session creation/hook registration helpers.
- `SendChannel` stores channel attrs and outbound sequence `Slot` objects.
- `SessionRecord` owns session ID, client pointer, fore/back channels, credential, and sequence-aware compound helpers.

## Control Flow
`NFS4Client.__init__` initializes the RPC client for NFSv4, configures callback program metadata, stores minor version, server tag/implementation ID/verifier, connects to the server, and initializes client/session maps. `compound` creates a per-call test tag via stack inspection, packs `COMPOUND4args`, sends procedure 1, unpacks `COMPOUND4res`, optionally records summary output, and returns the decoded result.

Client/session setup starts with `new_client`, which sends `EXCHANGE_ID`, checks the expected status, creates a `ClientRecord`, and stores it by clientid. `ClientRecord.create_session` retries on `NFS4ERR_DELAY`, then `_add_session` increments the client sequence, creates a `SessionRecord`, and stores it in the dispatcher's session map.

Session compounds prepend `SEQUENCE`. `_prepare_compound` chooses a free foreground slot, generates a sequence op, and records the slot. `compound` sends `[SEQUENCE] + ops`, updates slot state from the SEQUENCE result, retries NFS4ERR_DELAY with special handling for delay on the SEQUENCE operation, marks the slot free, strips the sequence result on success, and returns the application-level response.

Callback flow unpacks `CB_COMPOUND4args`, creates a `CBCompoundState`, dispatches each callback op by generated name, appends encoded results, and stores replay-cache data when a callback `SEQUENCE` provides a cache object. `op_cb_sequence` validates position, session ID, slot ID, and sequence ID, then sets environment caching/session fields. Hook helpers allow tests to attach pre/post handlers per clientid and callback op.

## State And Persistence Behavior
The client stores process-local server connection, credentials, sessions, client records, verifier, callback hooks, slots, SSV contexts, and replay/cache state. It persists nothing to disk. Sequence slots are marked `inuse` for outbound calls and updated using `Slot.finish_call`. SSV contexts maintain key windows and are mutated by `set_ssv`.

## Dependencies And Integration Points
The module depends on `rpc.rpc`, `nfs4lib`, generated NFSv4 constants/types, SCTRL packers, `nfs_ops`, `nfs4commoncode` callback encoders, `nfs4server.Slot` and `Channel`, Python threading/hmac/inspect/logging, and security classes from `rpc.security`. It is used by client tests, data-server management, and pNFS callback/layoutrecall flows.

## Risks And Edge Cases
- The file imports `os.path.basename` but `create_tag` calls `os.fsencode` without importing `os`.
- There are two `handle_1` definitions; the second overwrites the first stub.
- `op_cb_compound` catches `NFS4Errror` with a misspelled name, so invalid UTF-8 tag handling may raise unexpectedly.
- `new_pnfs_client_session` calls `fail` but does not import it.
- Session `compound` assigns `saved_kwargs = kwargs` rather than copying; retry preparation mutates the same dict.
- Slot release happens after the retry loop, but exceptions before release can leak `inuse`.
- Many callback operations are stubs that return OK with empty or hook-provided results.
- State-protection errors sometimes raise strings.

## Test Signals
Signals include EXCHANGE_ID/CREATE_SESSION/RECLAIM_COMPLETE success, correct slot sequence increments and replay behavior, NFS4ERR_DELAY retry semantics, stripped SEQUENCE results, callback SEQUENCE validation, callback hook invocation, CB_LAYOUTRECALL triggering LAYOUTRETURN, SSV SET_SSV digest updates, and summary output matching issued operations.
