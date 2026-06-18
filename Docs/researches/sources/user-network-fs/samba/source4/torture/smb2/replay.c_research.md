<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/replay.c -->
# sources/user-network-fs/samba/source4/torture/smb2/replay.c

## Purpose
`replay.c` is the SMB2/SMB3 torture suite for replay semantics: how a server handles `SMB2_FLAGS_REPLAY_OPERATION`, DurableHandleReqV2 create GUID matching, persistent handle reconnect, multi-channel channel sequence numbers, lease/oplock break interactions, and corner cases where a replay arrives while an original create is still pending. The suite is intentionally both a conformance probe and a regression test for Samba bugs such as bug 14449, with paired "sane" and "windows" expectations where Windows behavior diverges from Samba's intended semantics.

## Important APIs, Types, And Functions
The core helpers are local macros `CHECK_VAL`, `CHECK_STATUS`, `CHECK_CREATED`, `CHECK_HANDLE`, `CHECK_CREATE_OUT`, and `WAIT_FOR_ASYNC_RESPONSE`; they convert protocol mismatches into torture failures and make replayed create responses comparable to earlier reference responses. The tests are registered from `torture_smb2_replay_init()` using `torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()`.

The high-level test families are:

- `test_replay_commands()` toggles replay mode on the current SMB2 session and verifies ordinary create, write, flush, read, setinfo, getinfo, ioctl, and lock operations still return expected statuses.
- `test_replay_regular()` proves regular creates without a create GUID are not de-duplicated by the replay flag.
- `test_replay_dhv2_oplock*()` and `test_replay_dhv2_lease*()` cover DurableHandleReqV2 single-channel replay with batch oplocks, leases, changed requested oplock/lease state, changed share modes, and mismatched lease keys.
- `_test_dhv2_pending1_vs_violation()`, `_test_dhv2_pending1_vs_hold()`, `_test_dhv2_pending2_vs_hold()`, and `_test_dhv2_pending3_vs_hold()` are matrix drivers for pending creates blocked behind lease or oplock breaks, including single-channel, disconnected multi-channel, and blocked-transport multi-channel cases.
- `test_channel_sequence_table()` and `test_channel_sequence()` exercise channel sequence number windows for write, ioctl, and setinfo with and without replay.
- `test_replay3()` through `test_replay7()` cover multi-channel durable create replay, I/O ordering, persistent handles, error-code behavior for duplicate create GUIDs, and a notify/cancel channel sequence regression.
- `test_durable_reconnect_replay1()`, `test_durable_reconnect_replay2()`, `test_durable_reconnect_replay3()`, and `test_replay_twice_durable()` cover reconnection and repeated replay behavior for durable or persistent lease-backed handles.

The file depends heavily on Samba SMB2 client structures and helpers: `struct smb2_tree`, `struct smb2_transport`, `struct smb2_session`, `struct smb2_create`, `struct smb2_handle`, `struct smb2_lease`, `struct smb2_lease_break_ack`, `struct smb2_break`, `struct smb2_request`, `union smb_fileinfo`, `union smb_setfileinfo`, `union smb_ioctl`, `smb2_create()`, `smb2_create_send()/recv()`, `smb2_lease_v2_create()`, `smb2_oplock_create_share()`, `smb2_session_channel()`, `smb2_session_setup_spnego()`, `smb2cli_session_start_replay()`, `smb2cli_session_stop_replay()`, `smb2cli_session_reset_channel_sequence()`, `smb2cli_session_increment_channel_sequence()`, and connection/tcon capability accessors.

## Control Flow
Most tests first require SMB 3.x because replay semantics, durable v2 opens, channel sequence checks, and multi-channel are SMB3-era behavior. Tests then create `replaytestdir`, unlink any target file, set oplock and lease break handlers, build a `struct smb2_create`, issue an original create, and either replay it immediately or force a conflicting server state before replaying.

Single-channel durable replay tests follow this pattern: create a file with `durable_open_v2 = true`, `persistent_open` as needed, and a random `create_guid`; save the successful output; call `smb2cli_session_start_replay()`; resend a create with the same GUID; stop replay; then verify either an exact replay response, an access-denied response for invalid oplock/lease substitution, or a duplicate-object status when the replay flag is absent. Share capability checks adjust expectations for scale-out shares, which may downgrade oplocks and deny durable handles.

The pending-create matrix drivers are more involved. Client 1 opens a file with a batch oplock or RWH lease and often with full sharing. Client 2 sends an asynchronous durable v2 create with a new create GUID and requested level of none, batch oplock, or lease. The driver waits until the create is pending behind an oplock or lease break, sends replayed creates on the same or other channels, observes the expected immediate rejection (`NT_STATUS_FILE_NOT_AVAILABLE` for Samba's sane behavior or `NT_STATUS_ACCESS_DENIED`/`NT_STATUS_SHARING_VIOLATION` in Windows-mode variants), releases the blocker by close or break acknowledgement, and then verifies the original pending create and a later replay either complete with matching handle/lease state or preserve the expected failure.

Multi-channel tests bind additional transports to the same session with `smb2_session_channel()`, manipulate channel sequence numbers, disconnect or block transports, and validate replay behavior as the server's notion of current and stale channel sequence changes. `test_channel_sequence_table()` walks explicit low, high, wraparound, and random channel sequence values around the allowed window and checks write/ioctl/setinfo acceptance.

Reconnect tests intentionally free or disconnect trees while durable or persistent opens remain server-side. They reconnect using saved transport options and sometimes a previous session id, then retry the create under replay and verify that the resurrected handle is usable with a write. `test_replay_twice_durable()` confirms a second replay after the handle has been used is treated as a normal open rather than a second durable reconnect.

## State And Persistence
The suite creates and deletes files below `replaytestdir` or random `lease_break-*.dat` paths. Durable and persistent handle state persists on the server across client-side tree/session teardown, connection loss, and reconnect. Replay identity is carried by create GUIDs plus SMB session/client identity, and replay mode is client-side state toggled on `smbXcli` sessions before selected requests.

Lease, oplock, and channel sequence state are central. The tests install global torture break handlers, set skip-ack flags to deliberately hold breaks pending, and track `break_info`/`lease_break_info` counts, transport identity, break level, lease key, lease epoch, and acknowledgement payloads. Multi-channel tests also mutate per-session channel sequence numbers and, in blocked-transport cases, manipulate transport blocking via the torture transport-blocking helpers.

Cleanup is explicit but complex: handles are closed when non-null, test directories are removed with `smb2_deltree()`, sessions/transports are disconnected in matrix tests, and replay mode is stopped in `done` paths where needed. Some tests call `talloc_free(tree)` or `TALLOC_FREE(tree)` because the torture registration hands in owned tree instances.

## Dependencies And Integration Points
This file integrates with the Samba torture harness, SMB2 client library, command-line credentials, resolver and loadparm configuration, event loop, security constants, and the SMB2 oplock and lease break handler test utilities. It requires working SMB3 negotiation and selectively requires server capabilities: `SMB2_CAP_LEASING`, `SMB2_CAP_MULTI_CHANNEL`, and `SMB2_CAP_PERSISTENT_HANDLES`; persistent handle tests also require continuously available shares, while several hold tests skip scale-out shares.

The suite is registered as the `smb2.replay` torture suite and is meant to run against Samba and Windows servers. The "windows" variants act as compatibility documentation rather than Samba's preferred behavior.

## Risks
These tests are timing-sensitive because they depend on asynchronous create requests reaching pending state, lease/oplock breaks not being auto-acknowledged too early, server request timeouts, and transport disconnect or blocking behavior. A slow or unusual server can turn expected statuses into timeouts. The matrix functions intentionally free or disconnect trees and transports; cleanup ordering is important to avoid use-after-free in the harness.

Expected status depends on negotiated dialect, share capabilities, persistent-handle support, leasing support, and whether the server follows Windows quirks. Scale-out and continuously available share behavior changes durable/persistent grant expectations. Random filenames, GUIDs, lease keys, and generated strings reduce collision risk but make failures harder to reproduce unless torture logs are kept.

## Test Signals
Important pass signals include exact replayed create output matching the original where required; no unexpected lease/oplock breaks during pure replay; correct `NT_STATUS_FILE_NOT_AVAILABLE`, `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_SHARING_VIOLATION`, `NT_STATUS_DUPLICATE_OBJECTID`, or `NT_STATUS_OK` status in the documented scenario; stable handle equality or inequality where asserted; correct durable/persistent output flags and 300-second durable timeout; correct lease key, epoch, and state; successful writes after durable reconnect; and no stale-channel writes, ioctls, or setinfo calls succeeding outside the allowed sequence window.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/replay.c -->
