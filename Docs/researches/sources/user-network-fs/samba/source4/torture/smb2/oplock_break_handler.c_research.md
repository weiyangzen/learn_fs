# sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.c

## Purpose
This helper file provides shared oplock-break state and reusable handlers for SMB2 torture tests outside `oplock.c`. It centralizes break acknowledgement, optional ack suppression, and short event-loop polling for tests that expect asynchronous oplock breaks.

## Important APIs, Types, And Functions
It defines the global `struct break_info break_info` declared in the header. `torture_oplock_ack_handler()` records the incoming handle, break level, count, and received transport; validates that the callback arrived on the expected transport; optionally skips acknowledgement when `break_info.oplock_skip_ack` is set; otherwise sends `smb2_break_send()` and receives completion in `torture_oplock_ack_callback()`. `torture_oplock_ignore_handler()` deliberately ignores break requests while still returning true to the transport callback path. `torture_wait_for_oplock_break()` uses a one-second tevent timer and loops until either a new break arrives or the timeout fires.

## Control Flow
Consumers reset `break_info`, install one of these functions into `tree->session->transport->oplock.handler`, and then trigger a conflicting SMB2 operation. On break notification, the ack handler populates `break_info.br.in`, logs with `torture_comment()`, and asynchronously sends the SMB2 break response. The wait helper snapshots the old break count, installs a timer on `tctx->ev`, and calls `tevent_loop_once()` while waiting for `break_info.count` to advance.

## State And Persistence
State is process-global and mutable through `break_info`: test context, skip-ack flag, last handle, last level, `struct smb2_break`, count, failure count/status, and received transport pointer. No filesystem state is changed by this helper, but it drives network protocol acknowledgements that alter server-side oplock state.

## Dependencies And Integration Points
The file depends on Samba SMB2 client structures and calls, the torture framework, `smbXcli_base`, `oplock_break_handler.h`, and tevent timers. It is intended for SMB2 torture tests that need consistent break tracking; users must set `break_info.tctx` through `torture_reset_break_info()` or otherwise before relying on log messages.

## Risks
The global `break_info` is not safe for concurrent independent tests. The ack callback assumes the original `break_info.br` remains the right receive object for the outstanding request. `torture_wait_for_oplock_break()` waits only one second, so slow or blocked servers can produce false negatives. `torture_oplock_ignore_handler()` does not increment counters, so tests using it cannot infer whether a break arrived from `break_info`.

## Test Signals
Expected signals include `break_info.count` increments, `break_info.level` matching the server-requested downgrade, `break_info.failures == 0` after ack completion, `break_info.failure_status` on failed ack receive, and `break_info.received_transport` matching the tree transport.
