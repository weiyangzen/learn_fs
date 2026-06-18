# sources/user-network-fs/samba/source4/torture/smb2/durable_open.c

## Purpose
`durable_open.c` implements the SMB2 durable-handle torture suites. It verifies when durable opens are granted, how durable handles reconnect after TCP disconnects, session reconnects, tree disconnects, logoff, alternate users, conflicting opens, oplock or lease breaks, byte-range locks, delete-on-close, file position, allocation size, read-only attributes, and stat-only opens. It covers both oplock-backed durable handles and lease-backed durable handles, including lease v2 reconnect request/response paths.

The file is test code, but it encodes important protocol expectations: durable state is only granted for a batch oplock or handle lease, reconnect is driven by the durable handle blob plus lease identity where applicable, many create fields are ignored during reconnect, and some reconnect failures must preserve the original durable state.

## Important APIs, Types, And Functions
The file uses SMB2 create, close, write, lock, setinfo/getinfo, logoff, tree disconnect, tree connect, session setup, and connection extension helpers. It also uses `smb2cli_conn_server_capabilities()` for lease support detection, `smb2cli_session_current_id()` for previous-session reconnects, `smb2_connect()` for reconnecting as another user, and loadparm/resolve/credential helpers for alternate-user tests.

Assertion and response-checking macros are central:

- `CHECK_STATUS()` asserts exact NTSTATUS values.
- `CHECK_CREATED()` validates create action, zero size, file attributes, and reserved fields.
- `CHECK_CREATED_SIZE()` also validates allocation size and file size.
- `CHECK_VAL()`, `CHECK_NOT_VAL()`, and `CHECK_NOT_NULL()` keep repeated checks compact.

Important data tables are:

- `durable_open_vs_oplock_table`, covering no oplock, shared, exclusive, and batch oplocks against all share-mode combinations. Only batch oplocks are expected to grant durable state.
- `durable_open_vs_lease_table`, covering no lease, read, read/write, read/handle, and read/handle/write leases against all share-mode combinations. Only handle leases (`RH` and `RHW`) are expected to grant durable state.

Representative test groups are:

- Open grant matrix: `test_durable_open_open_oplock()`, `test_durable_open_open_lease()`.
- Basic reconnect behavior: `reopen1`, `reopen1a`, `reopen1a_lease`, `reopen2`, `reopen2_lease`, `reopen2_lease_v2`, `reopen2a`, `reopen3`, `reopen4`, `reopen5`, and `reopen6`.
- Persistent handle state: `delete_on_close1`, `delete_on_close2`, `file_position`, `alloc_size`, and `read_only`.
- Conflict and locking cases: `oplock`, `lease`, `lock_oplock`, `lock_lease`, `lock_noW_lease`, `open2_lease`, and `open2_oplock`.
- Other coverage: `oplock_disconnect` leaves a disconnected durable handle behind for disconnect-specific testing, and `stat_open` verifies a read-attribute durable open with a lease.

Suite registration is split between `torture_smb2_durable_open_init()` for the normal `durable-open` suite and `torture_smb2_durable_open_disconnect_init()` for the one-test `durable-open-disconnect` suite.

## Control Flow
Most tests allocate a talloc context, generate a randomized filename to avoid stale state, remove any previous file of that name, create a file with either `smb2_oplock_create*()` or `smb2_lease_create*()`, set `io.in.durable_open = true`, validate the create response, then intentionally destroy or replace SMB2 connection objects to simulate disconnect scenarios.

The open-grant matrix tests are table-driven. Each row builds a create request with a specific oplock or lease state and share mode, requests durable open, and checks `io.out.durable_open` against the expected boolean while also verifying the granted oplock/lease state.

The reconnect tests vary the way the original connection is interrupted:

- `reopen1` attempts a durable reconnect on the same live connection while the original handle is still active and expects `NT_STATUS_OBJECT_NAME_NOT_FOUND`.
- `reopen1a` reconnects a session on another TCP connection with previous session ID; the old session is deleted and durable reconnect succeeds on the new session. For oplocks, a different client GUID is allowed.
- `reopen1a_lease` performs the same pattern for leases but requires the original client GUID for successful durable reconnect; a different GUID fails.
- `reopen2` frees the tree to simulate TCP disconnect, reconnects normally, and reclaims the durable handle. It then demonstrates that filename and most create fields are ignored for oplock durable v1 reconnect and that an extra durable-open request context is ignored.
- `reopen2_lease` and `reopen2_lease_v2` require the lease request and lease key for reconnect; missing lease context, wrong lease key, or wrong filename fails, while the requested lease state is irrelevant.
- `reopen2a` reconnects using the previous session ID and then reclaims the durable handle.
- `reopen3` tree-disconnects and reconnects a new tree on the same session, expecting durable reconnect failure.
- `reopen4` logs off, creates a new session and tree on the same transport, and expects durable reconnect success.
- `reopen5` verifies that a failed durable reconnect from another process does not clobber a later valid reconnect of the original durable open state.
- `reopen6` reconnects as a different user and expects `NT_STATUS_ACCESS_DENIED`, then reconnects with the original credentials and succeeds.

State-preservation tests create a durable handle, mutate handle or file state, disconnect, reconnect, and verify state after durable reopen. `file_position` sets `RAW_SFILEINFO_POSITION_INFORMATION` to `0x1000` and checks it survives. `alloc_size` checks initial allocation, one-byte write, and expansion beyond the allocation step. `read_only` creates a read-only durable file, writes through the existing handle, reconnects, confirms read-only attributes and size, then restores attributes for cleanup.

Conflict tests use two tree connections. They disconnect the original durable owner, allow a second connection to open the file or take a new oplock/lease, then verify the original durable owner can no longer reclaim the stale handle. Lock tests take byte-range locks before disconnect and verify reconnect either preserves unlockability (`lock_oplock`, `lock_lease`) or fails when the lease lacks write caching (`lock_noW_lease`).

## State And Persistence Behavior
Durable open state is remote server state. The tests intentionally free client-side `struct smb2_tree` objects with `TALLOC_FREE()` or `talloc_free()` to simulate lost TCP transports while leaving durable server handles eligible for reconnect. The durable handle value is kept in a local `struct smb2_handle` and reused as `io.in.durable_handle` or `io.in.durable_handle_v2`.

Lease-backed durable reconnects persist identity through both the durable handle and lease key. The tests check `lease_key.data[0]`, `lease_key.data[1]`, lease state, lease flags, and lease duration after reconnect. Lease v2 tests use `lease_response_v2` and `lease_request_v2` but retain the same behavioral expectations.

Several tests validate persistence of associated handle/file state: delete-on-close should delete disconnected handles in one path but survive until close after successful reconnect in another; current file position survives durable reconnect; byte-range locks remain attached to the durable handle; allocation and size are preserved across reconnects; read-only attributes remain visible while an existing handle can still write.

Client object ownership is intentionally unusual. Many tests consume the passed `tree` by freeing it and replacing it with a new connection. Cleanup paths must therefore check whether `tree`, `tree1`, `tree2`, or `tree3` is non-NULL before closing handles and unlinking. Random filenames reduce stale-state collision risk, and most tests unlink before and after execution.

## Dependencies
The file depends on SMB2 server support for durable handles, batch oplocks, leases, session reconnect, tree disconnect, logoff, byte-range locks, delete-on-close, allocation-size reporting, DOS attributes, and reconnect semantics. Lease tests skip when `SMB2_CAP_LEASING` is absent. `reopen6` skips when secondary user credentials are anonymous or unavailable.

Important helper dependencies include `smb2_oplock_create()`, `smb2_oplock_create_share()`, `smb2_lease_create()`, `smb2_lease_create_share()`, `smb2_lease_v2_create()`, `smb2_util_share_access()`, `smb2_util_oplock_level()`, `smb2_util_lease_state()`, `torture_smb2_connection()`, `torture_smb2_connection_ext()`, `torture_smb2_tree_connect()`, and `torture_smb2_session_setup()`.

The alternate-user test depends on `torture_setting_string()` for `host` and `share`, `torture_user2_credentials()`, `smb2_connect()`, resolve context, socket options, and GENSEC settings.

## Integration Points
`torture_smb2_durable_open_init()` registers the suite as `smb2.durable-open` via the top-level SMB2 suite. It includes one-connection tests and two-connection tests using `torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()`. `torture_smb2_durable_open_disconnect_init()` registers `smb2.durable-open-disconnect.open-oplock-disconnect`, a targeted disconnect case.

These tests integrate with server code paths for SMB2 create contexts (`DURABLE_HANDLE_REQUEST`, reconnect contexts, lease contexts), session lifetime, tree lifetime, share-mode and oplock/lease arbitration, persistent open records, VFS open state, byte-range lock state, and file metadata persistence. They are high-value regression tests for changes in SMB2 handle databases and clustered or persistent-handle storage.

## Risks
The tests are precise about Windows/Samba-compatible status codes. Small server changes that preserve broad behavior but return a different error such as `INVALID_PARAMETER` versus `OBJECT_NAME_NOT_FOUND` will fail these tests. That strictness is useful for protocol compatibility but can make backend-specific behavior visible.

Some cleanup paths are fragile because the tests deliberately free and replace connection objects. For example, there are paths that may attempt to close or unlink through a tree pointer selected after earlier frees, and several tests assign `h = io.out.file.handle` after an expected failing create even though the handle may be empty. The common pattern works under expected server behavior but should be reviewed carefully if adding new early exits.

`test_durable_open_open2_oplock()` appears to call `CHECK_CREATED(&io1, CREATED, FILE_ATTRIBUTE_ARCHIVE)` after creating the second open with `io2`; this looks like a copy/paste mistake in the assertion target. `reopen5` includes an explicit `sleep(3)` to wait for record/destructor behavior, making it timing-sensitive and slow. Lease tests use `random()` lease keys without explicitly seeding in this file, relying on surrounding process behavior.

Durable-handle tests can leave server-side durable state behind if the process aborts at the wrong point. Random filenames reduce collision risk but do not replace cleanup. The suite also assumes support for batch oplocks or leases depending on the test; lease tests skip on missing capability, but oplock behavior differences across servers may still produce failures.

## Test Signals
Core pass signals include `io.out.durable_open` being true only for batch oplocks or handle leases, exact create actions (`CREATED` versus `EXISTED`), correct file attributes and sizes after reconnect, correct lease key/state echoes, and exact reconnect failure statuses for same-session, wrong-GUID, wrong-lease-key, wrong-user, tree-disconnect, and conflicting-open cases.

Important persistence signals are successful durable reopen after TCP disconnect, `NT_STATUS_FILE_CLOSED` when querying an old handle before reconnect, preserved file position `0x1000`, successful unlock of a byte-range lock after reconnect, delete-on-close behavior matching whether the handle was reconnected, allocation-size growth after writes, and read-only attributes preserved after reconnect.

Operational signals include skips for missing leasing capability or missing user2 credentials, warnings when reconnect setup fails, and clean removal of randomized test files. The disconnect-specific suite intentionally leaves the server to handle a disconnected durable open without a normal reconnect path.
