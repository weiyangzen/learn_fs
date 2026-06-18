# sources/user-network-fs/samba/source4/torture/smb2/durable_v2_open.c

## Purpose

This file defines Samba torture suites for SMB2 durable handle v2, persistent handle, lease, oplock, reconnect, and reconnect-delay behavior. It is not production server code; it is a protocol conformance and regression test harness that drives `smb2_create`, reconnects sessions or transports, and asserts that server-side open state is preserved, rejected, downgraded, purged, or timed out according to SMB2 durable v2 semantics.

The file exports three suite initializers: `torture_smb2_durable_v2_open_init()`, `torture_smb2_durable_v2_delay_init()`, and `torture_smb2_durable_v2_regressions_init()`. These register individual tests under the `durable-v2-open`, `durable-v2-delay`, and `durable-v2-regressions` suite names.

## Important APIs, Types, And Helpers

The tests are built around Samba's SMB2 client/torture APIs:

- `smb2_create`, `smb2_close_send`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, `smb2_lock`, `smb2_write`, `smb2_setinfo_file`, and `smb2_util_write` perform protocol operations against a test share.
- `torture_smb2_connection()` and `torture_smb2_connection_ext()` establish fresh connections, optionally reusing a previous session id and customized `smbcli_options`.
- `smb2_oplock_create_share()`, `smb2_lease_create()`, `smb2_lease_create_share()`, `smb2_lease_v2_create()`, `smb2_generic_create()`, and `smb2_generic_create_share()` populate `struct smb2_create` requests for the relevant open style.
- `smb2cli_tcon_capabilities()` and `smb2cli_conn_server_capabilities()` gate behavior on share capabilities such as continuous availability, scaleout, and leasing.
- `torture_lease_handler`, `lease_break_info`, `CHECK_NO_BREAK`, `CHECK_BREAK_INFO_V2`, and `torture_reset_lease_break_info()` integrate with `lease_break_handler.h` to validate lease break side effects.

Local assertion macros centralize expected protocol results:

- `CHECK_STATUS(status, correct)` and `CHECK_VAL(v, correct)` fail the current test through the `done:` cleanup path.
- `CHECK_CREATED(io, created, attr)` validates `create_action`, size, file attributes, and reserved fields.
- `CHECK_LEASE_V2(io, state, oplevel, key, flags, parent, epoch)` validates v2 lease response shape, key, state, flags, parent lease key, duration, and epoch.

The local `break_info` object plus `torture_oplock_handler()` and `torture_oplock_close_callback()` capture an oplock break path for the AppInstanceId test. The handler increments a counter and asynchronously closes the broken handle.

The main table-driven types are `struct durable_open_vs_oplock` and `struct durable_open_vs_lease`. Their tables encode combinations of requested oplock/lease level, share mode, and expected durable or persistent grant. Separate continuous-availability tables expect persistent handles when the share advertises `SMB2_SHARE_CAP_CONTINUOUS_AVAILABILITY`.

## Control Flow

The suite starts with table-driven grant checks. `test_durable_v2_open_create_blob()` verifies durable v2 create contexts, scaleout-share differences, default timeout normalization, and invalid combinations of durable-request and durable-reconnect blobs. `test_durable_v2_open_oplock()` and `test_durable_v2_open_lease()` iterate all encoded share/access combinations. They assert that durable v2 is granted only with batch oplocks or handle-capable leases, with scaleout shares downgrading batch to level II and suppressing non-persistent durable handles.

The reconnect tests then exercise progressively more realistic failure and recovery paths:

- `reopen1` proves reconnecting a still-live open on the same connection fails.
- `reopen1a` and `reopen1a-lease` reconnect sessions using `previous_session_id`; oplock durable reconnects tolerate a different client GUID, while lease-based durable reconnects require the original client GUID.
- `reopen2`, `reopen2b`, and `reopen2c` simulate TCP disconnects and test the v2/v1 reconnect matrix. V2 reconnect requires the original create GUID, while v1 reconnect can recover a v2-created durable handle in one compatibility path. A v1-created durable handle cannot be recovered through the v2 reconnect path.
- `reopen2-lease` and `reopen2-lease-v2` add lease key validation, required filename validation, and show that many create parameters are ignored during reconnect once the durable handle, create GUID, filename, and lease key are correct.

The lock and lease-state tests add durable state with byte-range locks and competing opens. `lock-oplock` and `lock-lease` prove a byte-range lock survives disconnect and can be unlocked after reconnect. `lock-noW-lease` demonstrates that a durable reconnect after a byte-range lock fails when the lease lacks write caching. `stat-and-lease`, `nonstat-and-lease`, and `statRH-and-lease` check how preexisting opens and stat-like access affect lease downgrades from `RWH` to `RH`.

The multi-handle tests validate disconnected handle retention and purging:

- `two-same-lease` and `two-different-lease` keep multiple durable opens through disconnect and reconnect.
- `keep-disconnected-rh-with-*` cases show disconnected read/handle leases can remain reconnectable when a second connection does a stat open, an `RH` durable open, an `RWH` open downgraded to `RH`, or an `RWH` disconnected handle coexists with a stat open.
- `purge-disconnected-rwh-with-*` and `purge-disconnected-rh-with-*` cases show when later opens, share-none opens, writes, or renames purge disconnected durable handles and make reconnect return `NT_STATUS_OBJECT_NAME_NOT_FOUND`.

The remaining suite entries cover special cases. `test_durable_v2_open_app_instance()` verifies that a second durable open with the same AppInstanceId replaces the first server-side open and the first close returns `NT_STATUS_FILE_CLOSED`. `test_persistent_open_oplock()` and `test_persistent_open_lease()` reuse the durable table runners with persistent requests and switch expectations based on continuous availability and scaleout capabilities. `test_durable_v2_setinfo()` is a regression test for reconnect after setting end-of-file information. `test_reconnect_twice()` verifies that reconnecting a durable handle twice refreshes the scavenger timeout rather than letting the first disconnect timer purge the second disconnected handle.

The delay and regression suites are registered separately. `test_durable_v2_reconnect_delay()` checks a zero timeout durable v2 open can reconnect immediately. `test_durable_v2_reconnect_delay_msec()` uses a one millisecond timeout, sleeps, and expects reconnect failure. `test_durable_v2_reconnect_bug15624()` requires `--option=torture:bug15624=yes` and a configured `error_inject` VFS module, then asserts a failed reconnect does not deadlock later unlink cleanup.

## State And Persistence Behavior

The persistent state under test is server durable-open state, not local file content alone. Each test creates a unique randomized filename or per-test directory, records the returned durable handle and create GUID, frees the SMB tree to simulate disconnect, and later attempts reconnect with the saved handle material. Success is detected by `NT_STATUS_OK`, `NTCREATEX_ACTION_EXISTED`, preserved oplock or lease response, and continued ability to close, unlock, write, or delete.

Lease tests also persist client-side `struct smb2_lease` values across reconnect. Correct lease key, create GUID, filename, and sometimes original client GUID are required to recover the server-side durable handle. The tests deliberately mutate lease keys, filenames, create GUIDs, and requested lease states to prove which fields are authoritative and which are ignored.

Cleanup is explicit and defensive. Most tests track handles through pointer variables set to `NULL` when a handle is intentionally invalidated or transferred. `done:` blocks close non-null handles, unlink test files, remove per-test directories, send keepalives where needed to drain break handling, and free SMB trees and talloc contexts. Random filenames reduce collisions if a previous run left state behind.

## Dependencies And Integration Points

This file depends on Samba torture infrastructure and SMB2 client libraries from `includes.h`, `libcli/smb2/smb2.h`, `libcli/smb2/smb2_calls.h`, `smbXcli_base.h`, `torture/torture.h`, `torture/smb2/proto.h`, `librpc/ndr/libndr.h`, and `lease_break_handler.h`.

The suites integrate with the broader torture runner through `torture_suite_add_1smb2_test()`, `torture_suite_add_2smb2_test()`, and `torture_suite_create()`. Several tests require server capabilities: leasing tests skip without `SMB2_CAP_LEASING`; persistent-handle expectations depend on `SMB2_SHARE_CAP_CONTINUOUS_AVAILABILITY`; scaleout shares alter oplock and durable-handle expectations through `SMB2_SHARE_CAP_SCALEOUT`.

The regression test for bug 15624 integrates with a special server setup using `vfs objects = error_inject` and `error_inject:durable_reconnect=st_ex_nlink`; without the `torture:bug15624` setting it skips rather than producing a false failure.

## Risks And Edge Cases

The tests rely on timing in delay and scavenger cases. `sleep(4)`, `sleep(2)`, and `sleep(10)` make the tests sensitive to slow servers, scheduler delays, and durable-handle cleanup implementation details. The intent is clear, but failures in these cases may require examining timing before assuming protocol logic is wrong.

Several scenarios depend on exact server capability advertisement. A share configured as scaleout or continuous availability changes the expected durable/persistent outcome. Running the same test matrix against a differently configured share can produce expected divergences.

The tests intentionally free `tree` to simulate disconnect and later may use another tree for cleanup. Incorrect cleanup tree selection can leave files behind, especially after tests that set pointers to `NULL` because a reconnect attempt should have invalidated a handle. Most paths are careful, but interrupted runs can still leave randomized files.

Lease break tests assume the registered lease handler sees and records breaks in the expected order and that `smb2_keepalive()` drains pending notifications. Races in notification delivery could surface as test flakiness rather than durable-open logic errors.

The file is large and repetitive. Many tests differ only by lease state, competing open type, or expected status. Changes to helper macros or table entries can affect a broad test surface.

## Test Signals

Strong pass signals include exact NTSTATUS matches for invalid reconnect combinations, preservation of returned handle state after disconnect, correct absence of durable-query response blobs on reconnect, expected lease epoch increments, and correct lease break records for writes and renames.

Important negative signals include unexpected durable grants for non-batch oplocks, missing persistent grants on continuous-availability shares, reconnect success with wrong create GUID or lease key, reconnect failure after a valid durable disconnect, stale timeout purge after a successful intermediate reconnect, and deadlock or timeout during bug 15624 cleanup.

Capability-sensitive skips are expected for leasing-disabled servers and for the bug 15624 regression unless the required torture option and VFS error injection are configured.
