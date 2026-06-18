# sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.c

## Purpose
`lease_break_handler.c` implements the shared SMB2 torture lease-break callback machinery used by lease and multichannel tests. It records the last lease break notification, optionally acknowledges it, optionally closes a handle when a handle-caching lease is revoked, counts callbacks and failures, and provides a bounded event-loop wait helper for tests that expect an asynchronous break.

## Important APIs, Types, and Functions
The file defines the global `struct lease_break_info lease_break_info`, declared in `lease_break_handler.h`. `torture_lease_handler()` is the transport-level lease break handler installed on `struct smb2_transport`. It consumes `struct smb2_lease_break` notifications, records the transport and break payload, increments `count`, closes `lease_break_info.lease_handle` with `smb2_close_send()` when a HANDLE lease is removed, and sends `smb2_lease_break_ack_send()` when `SMB2_NOTIFY_BREAK_LEASE_FLAG_ACK_REQUIRED` is set and `lease_skip_ack` is false. `torture_wait_for_lease_break()` spins the test event loop until a new break arrives or a one-second timer fires. The async receive callbacks update `lease_break_ack`, `close`, and `failures`.

## Control Flow
A server lease break enters through `torture_lease_handler()`. The handler converts the new lease state to a diagnostic string, stores the notification in global test state, and chooses one of three paths: close a stored handle for handle-lease revocation, deliberately skip acknowledgment for retry/timing tests, or asynchronously send a lease-break acknowledgment. `torture_wait_for_lease_break()` snapshots the old count, installs a `tevent` timer on `tctx->ev`, and loops with `tevent_loop_once()` until `count` advances or the timer sets `timesup`.

## State and Persistence Behavior
All state is process-local torture state in the global `lease_break_info`. There is no durable persistence; the state is reset by `torture_reset_lease_break_info()` from the header. Asynchronous acknowledgments and closes are stored into the global struct after their send requests complete, so tests must continue the event loop before inspecting ack output.

## Dependencies and Integration Points
The code depends on Samba SMB2 client calls, `tevent`, torture assertions/logging, `smbXcli_base`, and the lease helper declarations in `lease_break_handler.h`. `multichannel.c` installs this handler on each bound channel to verify which transport receives lease breaks and whether breaks can be acknowledged on another channel.

## Risks and Edge Cases
The global singleton means concurrent lease tests would interfere with each other. The close-on-handle-revocation path returns before sending an explicit lease ack, so correctness depends on the close being the intended response for that scenario. The wait helper treats timeout as diagnostic rather than fatal, leaving each caller to assert count/failure expectations. Async send failures are counted only after the callback runs.

## Test Signals
Consumers assert `lease_break_info.count`, `failures`, recorded transport, break state, epoch, and ack contents through macros in the header. Retry tests intentionally set `lease_skip_ack` or block transports to verify timeout/retry behavior.
