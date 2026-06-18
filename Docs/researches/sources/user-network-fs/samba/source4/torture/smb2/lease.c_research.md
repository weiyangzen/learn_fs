# sources/user-network-fs/samba/source4/torture/smb2/lease.c

## Purpose

`lease.c` is the SMB torture coverage for SMB2 file leases and SMB3 directory leases. It registers two suites, `smb2.lease` and `smb2.dirlease`, and exercises how a server grants, upgrades, downgrades, breaks, acknowledges, times out, and preserves lease state across creates, writes, locks, renames, deletes, disconnects, and multi-client contention.

The file is almost entirely black-box protocol validation. It builds SMB2 create/setinfo/lock/write requests, installs lease and oplock break handlers, then checks exact `NTSTATUS`, create action, oplock level, lease key, lease state, lease flags, parent lease key, and SMB3 lease epoch values. Most tests require `SMB2_CAP_LEASING`; directory lease cases also require `SMB2_CAP_DIRECTORY_LEASING`, and v2 lease cases skip below `PROTOCOL_SMB3_00`.

## Important APIs, Types, and Helpers

- `struct smb2_create`, `struct smb2_lease`, `struct smb2_handle`, `struct smb2_write`, `struct smb2_lock`, `union smb_setfileinfo`, and `struct smb2_request` are the main request/response carriers.
- `smb2_lease_create()`, `smb2_lease_create_share()`, `smb2_lease_v2_create()`, and `smb2_lease_v2_create_share()` construct create requests with SMB2 lease create contexts. The v2 variants add parent lease keys and lease epoch fields.
- `smb2_create()`, `smb2_create_send()`, and `smb2_create_recv()` are used for synchronous opens and deferred/conflicting async opens.
- `smb2_lease_break_ack()` acknowledges lease breaks and validates server responses for accepted, rejected, stale, or unsolicited acknowledgements.
- `smb2_setinfo_file()` and `smb2_setinfo_file_send()/recv()` drive rename, hardlink, delete-on-close, EOF, and basic-info changes that should or should not break leases.
- `smb2_lock()`, `smb2_write()`, `smb2_util_write()`, `smb2_util_close()`, `smb2_util_unlink()`, `smb2_deltree()`, and `torture_smb2_connection_ext()` provide filesystem setup, cleanup, byte-range locking, writes, and extra connections/client GUIDs.
- `CHECK_VAL`, `CHECK_STATUS`, `CHECK_CREATED`, `CHECK_LEASE`, and `CHECK_LEASE_V2` are local assertions for status, create metadata, v1 lease responses, and v2 lease responses.
- `lease_break_handler.h` supplies shared `lease_break_info`, `torture_lease_handler`, `torture_wait_for_lease_break`, `CHECK_NO_BREAK`, `CHECK_BREAK_INFO`, `CHECK_BREAK_INFO_V2`, `CHECK_BREAK_INFO_V2_NOWAIT`, `CHECK_LEASE_BREAK`, and `CHECK_LEASE_BREAK_ACK`.
- `torture_oplock_handler()` and `torture_oplock_break_callback()` are local oplock-break tracking helpers used to validate lease/oplock interaction.
- Static lease keys `LEASE1` through `LEASE4` and directory lease keys `DLEASE1` through `DLEASE3` make lease-key identity checks deterministic.

## Control Flow and Test Coverage

The first half registers `torture_smb2_lease_init()` as the `lease` suite. It covers:

- Basic lease requests: files accept common R/H/W combinations, directories reject normal file leases unless directory leasing is negotiated, alternate data streams can be leased under separate keys, and duplicate lease keys on different files fail with `NT_STATUS_INVALID_PARAMETER`.
- Upgrade behavior: uncontended upgrades only change state when the new request is a valid strict superset; contended upgrades are allowed only if the upgraded state can coexist with the second lease and must not cause a break.
- Lease break matrices: `break_results`, `oplock_results`, and `oplock_results_2` encode expected downgrade/grant combinations for lease-vs-lease and lease-vs-oplock contention.
- Self and stat-open behavior: writes through one handle should not spuriously break the same lease key, but should break other keys; pure attribute/stat opens are classified by access mask and should preserve RWH leases where Windows-compatible behavior expects no break.
- Pending-break behavior: `breaking1` through `breaking6` and `v2_breaking3` defer ACKs with `lease_skip_ack`, verify `SMB2_LEASE_FLAG_BREAK_IN_PROGRESS`, check pending async requests, validate ACK state restrictions, and test multi-stage downgrades from RWH to RH/R/NONE.
- SMB3 v2 lease behavior: parent lease key flags, ignored parent keys without `SMB2_LEASE_FLAG_PARENT_LEASE_KEY_SET`, `SMB2_LEASE_FLAG_BREAK_IN_PROGRESS`, v1/v2 interop, and exact lease epoch increments.
- Locking and share-mode interaction: byte-range locks break conflicting leases only when they are backed by file data; overwrite creates and sharing violations drive specific downgrades.
- Multi-connection/client behavior: same-client-guid reconnects and different-client-guid connections distinguish lease sharing, breaking, and durable open behavior.
- Rename, unlink, timeout, and disconnect behavior: pending renames wait for ACKs, target-overwrite renames break target leases before `ACCESS_DENIED` or success, unlinks/delete-on-close break handle or directory leases at the correct time, skipped ACKs eventually time out, and disconnect/logoff/tree-disconnect paths are covered.
- Regression cases: `v1_bug15148`, `v2_bug15148`, `lease-epoch`, and `two-leases` pin down previously fragile edge cases around repeated writes after breaks, ungranted v2 lease epochs, and redispatched deferred opens.

The second half registers `torture_smb2_dirlease_init()` as the `dirlease` suite. It covers:

- Directory lease grant rules: directory oplock requests are reduced to `SMB2_OPLOCK_LEVEL_NONE`, while directory lease requests grant at most RH/R and never W.
- Parent lease key semantics: file creates, writes, closes, setinfo changes, renames, hardlinks, overwrites, and unlink-on-close operations avoid breaking the parent directory lease only when the child handle carries the correct parent lease key.
- Metadata mutation: the shared `test_dirlease_setinfo()` runs EOF, DOS attribute, birth time, modify time, change time, and access time updates from the same and a second client, each with correct, bad, and absent parent keys.
- Directory rename and open-file behavior: table-driven cases check whether open child file handle leases are broken and whether closing on break allows the directory rename to succeed.
- Unlink variants: explicit delete-on-close and initial `NTCREATEX_OPTIONS_DELETE_ON_CLOSE` are tested for matching vs mismatching parent lease keys and last-handle-close behavior.

## State and Persistence Behavior

The tests model lease state as server-side cache consistency state tied to a lease key, file object, client GUID, open handle, and sometimes a parent directory lease key. They assert that state persists across multiple opens using the same key, can be queried by creating again with the same key, can be upgraded only under strict compatibility rules, and is downgraded asynchronously via break notifications when a conflicting operation appears.

For SMB3 v2 leases, `lease_epoch` is part of the persistent state. The tests manually track expected epoch increments after opens, upgrades, and breaks, and explicitly verify that ungranted leases return the request epoch unchanged. Parent lease keys are also stateful: a child file handle opened with the correct parent directory lease key can mutate the file without breaking that directory lease, while bad or absent parent keys cause directory lease breaks.

Several tests intentionally keep break ACKs pending or absent. In those paths, the state remains in `BREAK_IN_PROGRESS`, same-key opens still report the current lease with the break flag, conflicting async opens remain pending where required, and late/invalid ACKs return specific error statuses. Timeout tests confirm the server can force progress and clear lease state after unacknowledged breaks.

The source cleans persistent test artifacts aggressively with `smb2_util_unlink()`, `smb2_util_rmdir()`, and `smb2_deltree()`, but it does mutate torture configuration in `test_lease_dynamic_share()` by changing `torture:share` to `dynamic_share` and restoring it afterward.

## Dependencies and Integration Points

- Built into the `TORTURE_SMB2` module by `source4/torture/smb2/wscript_build`, alongside `lease_break_handler.c`.
- Added to the root SMB2 torture suite in `source4/torture/smb2/smb2.c` through `torture_smb2_lease_init(suite)` and `torture_smb2_dirlease_init(suite)`.
- Depends on Samba SMB2 client library headers (`libcli/smb2/smb2.h`, `smb2_calls.h`, `smbXcli_base.h`), torture APIs (`torture/torture.h`, `torture/smb2/proto.h`, `torture/util.h`), security/access constants, tevent, loadparm, and the shared lease break handler.
- The tests are transport-sensitive because they install handlers directly on `tree->session->transport->lease` and `transport->oplock`. Some v2 assertions also verify which transport received the break.
- Test execution depends on server capabilities, negotiated dialect, target type (`TARGET_IS_SAMBA3` for dynamic shares), support for durable opens, directory leases, and configured torture shares.

## Risks and Edge Cases

- The file uses one global `lease_break_info`; tests must reset it before each scenario. Missing resets or extra async break delivery would make assertions order-dependent.
- Many cases depend on exact Windows-compatible behavior, including downgrade matrices, access-mask classification for stat opens, and lease epoch increments. Server changes that are locally reasonable can still fail these compatibility tests.
- Async tests rely on request state (`SMB2_REQUEST_RECV`, `SMB2_REQUEST_DONE`), `cancel.can_cancel`, tevent dispatch, timeouts, and sleeps. They can expose races if server break delivery timing changes.
- Directory lease tests are sensitive to parent lease key flags. The same child operation can legitimately produce no break, one break, or two breaks depending on whether keys match source/destination parents.
- Cleanup must tolerate handles that may or may not have opened after expected failures. Many tests use zeroed handles or `smb2_util_handle_empty()` guards, but a failed assertion before cleanup can leave files until the next run removes them.
- `test_lease_dynamic_share()` changes global torture configuration and uses sleeps to force different dynamic paths, so it is more environment-dependent than most tests.
- Multi-connection tests distinguish same vs random `client_guid`; changing connection helper defaults can alter lease sharing behavior.

## Test Signals

The direct test signals are the registered smb torture cases:

- `smb2.lease.request`, `break_twice`, `nobreakself`, `statopen*`, `upgrade*`, `break`, `oplock`, `multibreak`, `breaking*`, `v2_breaking3`, `lock*`, `sharing_violation`, `complex1`, `v2_complex*`, `v2_flags_*`, `v2_epoch*`, `v2_rename*`, `dynamic_share`, `timeout`, `unlink`, `timeout-disconnect`, `rename_wait`, `duplicate_*`, `v1_bug15148`, `v2_bug15148`, `initial_delete_*`, `rename_dir_openfile`, `lease-epoch`, and `two-leases`.
- `smb2.dirlease.v2_request_parent`, `v2_request`, `oplocks`, `leases`, `seteof`, `setdos`, `setbtime`, `setmtime`, `setctime`, `setatime`, `rename`, `rename_dst_parent`, `overwrite`, `hardlink`, and the four unlink parent-key cases.

Useful failure signatures include wrong `NTSTATUS`, wrong create action, unexpected or missing `CHECK_BREAK_INFO*`, wrong `SMB2_LEASE_FLAG_BREAK_IN_PROGRESS`, wrong v2 `lease_epoch`, break delivery on the wrong transport, async requests completing too early/late, or directory lease breaks occurring despite a correct parent lease key.
