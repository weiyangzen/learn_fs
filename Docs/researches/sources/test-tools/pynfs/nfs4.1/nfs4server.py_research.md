# sources/test-tools/pynfs/nfs4.1/nfs4server.py

## Purpose
`nfs4server.py` is the in-process pynfs NFSv4.1 server used by the test suite. It implements RPC program dispatch for NULL and COMPOUND, server control RPCs, client and session records, replay caches, state-protection scaffolding, filesystem mounting, NFSv4.1 operations, pNFS device/layout stubs, and callback transport helpers. It is intentionally test-oriented and includes many `STUB`, `BUG`, and draft-version notes.

## Important APIs, Types, and Functions
- `NFS4Server(rpc.Server)` is the main server. Key entry points are `handle_0`, `handle_1`, `op_compound`, `op_sequence`, `op_exchange_id`, `op_create_session`, filehandle operations, open/read/write/lock operations, pNFS operations, control operations, and callback helpers.
- `ClientList` maps both client owner ids and integer clientids to `ClientRecord` objects and allocates new clientids.
- `ClientRecord` stores client identity, verifier, principal, state protection, replay slot for `CREATE_SESSION`, session list, lease timestamp, and per-client stateid table.
- `SessionRecord` stores client association, sessionid, fore/back `Channel` objects, callback program, connection binding state, and nonce state.
- `Channel`, `Slot`, and `Cache` implement negotiated channel limits and DRC/replay behavior.
- `StateProtection` parses `SP4_NONE`, `SP4_MACH_CRED`, and `SP4_SSV` request state-protection args and provides `deny()` and `rv()` response helpers.
- `Recording` and `ctrl_*` functions support the separate server-control RPC used by pynfs tests to record, pause, reset, and grab traffic.

## Control Flow
Incoming COMPOUND calls enter `handle_1`, are unpacked with `FancyNFS4Unpacker`, passed to `op_compound`, then packed as `COMPOUND4res`. `op_compound` validates minor version and tag, dispatches each argop to `op_<name>`, appends encoded results, and stops at the first non-OK status. `NFS4Replay` is handled at the RPC level by waiting on the prior slot cache.

Session establishment starts with `op_exchange_id`, which implements draft case handling for new, unconfirmed, confirmed, rebooted, and update client records. `op_create_session` validates clientid, state protection, and create-session sequence, confirms the client when needed, negotiates channels, binds the fore channel to the current connection, optionally probes callback with `CB_NULL`, and registers the `SessionRecord`.

Most protocol operations call `check_session`, `check_cfh`, and sometimes `check_sfh`, then operate against `CompoundState` filehandles. OPEN dispatches by claim type into `open_claim_null` or `open_claim_fh`, then `open_file` coordinates share conflict testing, delegation recall, share-state creation, optional delegation grant, and MDS layout hooks.

## State and Persistence Behavior
Server state is in memory only. A restart or `reboot()` wipes sessions and client records and creates a fresh verifier. File state is delegated to `nfs4state.find_state` and each filesystem object's `state` field. Replay state is per-client for `CREATE_SESSION` and per-session fore-channel slot for `SEQUENCE`.

Lease tracking is represented by `ClientRecord.lastused`, but full grace-period and courtesy-client handling is mostly absent in this server implementation. The pNFS device table `devids` and filesystem registry `_fsids` are runtime maps populated by mounted filesystems.

## Dependencies and Integration Points
The module depends heavily on generated XDR constants/types in `xdrdef`, `nfs4lib` packing, `nfs4commoncode.CompoundState`, `nfs4state.find_state`, filesystem implementations in `fs`, server behavior knobs from `config`, and the local `rpc` framework. Export configuration is loaded dynamically by `read_exports`, whose Python module must provide `mount_stuff(server, opts)`. Server test modules interact with this file through NFS COMPOUNDs and through control/helper mechanisms such as `serverhelper`.

## Risks and Edge Cases
The code contains many incomplete protocol areas: GSS and SSV enforcement are stubs, size checks are stubs, UTF-8 validation is stubbed, session deletion is not fully synchronized, replay and client reboot semantics are incomplete, and pNFS layout operations are marked stubs. Several Python 2-era string assumptions remain visible, such as string-vs-bytes comparisons in some paths. `ClientRecord.principal_matches` references `env` without an argument, but the function does not appear to be used. `op_readlink`, `op_nverify`, and `op_verify` have suspicious error references (`NFS4_INVAL`, `e.code`) that should be treated as latent bugs.

Concurrency risk is high around state locks, file locks, delegation recall threads, and session/client deletion. Several comments explicitly note missing locking. The server is suitable as a test harness, not as a production NFS server.

## Test Signals
The adjacent `server41tests` modules exercise `EXCHANGE_ID`, `CREATE_SESSION`, `DESTROY_SESSION`, `DESTROY_CLIENTID`, COMPOUND validation, current stateid, block pNFS layout stateids, delegation recall, callback notification, courtesy expiry behavior, and copy semantics. The file also has runtime flags (`--use_block`, `--use_files`, `--is_ds`, `--show_summary`, `--debug_locks`) that drive integration tests.
