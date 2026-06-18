# sources/user-network-fs/samba/source4/torture/raw/mux.c

## Purpose
`mux.c` tests SMB1 request multiplexing around delayed operations. It verifies that blocking open, write, and lock requests interact correctly with close, unlock, cancel, and exit while multiple outstanding requests share one connection.

## Important APIs, Types, and Functions
- `test_mux_open()` checks delayed sharing-violation opens and `smb_raw_ntcancel()` behavior.
- `test_mux_write()` sends an async write into a locked range and expects `NT_STATUS_FILE_LOCK_CONFLICT`.
- `test_mux_lock()` checks blocking lock retry, cancel idempotence, and lock cancellation through session exit.
- `torture_raw_mux()` sets up `\\test_mux`, runs all subtests, exits the session, and deletes the directory.
- Uses raw `NTCREATEX`, `WRITEX`, `LOCKX`, close, cancel, and request receive APIs.

## Control Flow
The open test creates a file with restrictive share access, verifies a synchronous conflicting open delays about one second, sends two async conflicting opens, closes existing handles, cancels one request, and checks that one async open succeeds while the canceled one times out with sharing violation. The write test locks a byte range as one PID, sends a write as another PID, unlocks, then verifies the write reply remains a lock conflict. The lock test establishes conflicts, sends pending lock requests, unlocks or cancels them, and validates immediate completion semantics including repeated cancel and exit-driven cancellation.

## State and Persistence Behavior
State is limited to file handles, session PID mutations, raw request objects, and temporary files under `\\test_mux`. Locks are released through explicit unlocks or `smb_raw_exit()`.

## Dependencies and Integration Points
The file is registered through the raw torture entry point `torture_raw_mux()`. It uses the same SMB client session for most operations, intentionally relying on multiplexed outstanding requests over one transport.

## Risks and Edge Cases
- Timing assertions use narrow thresholds around expected one-second server delays and sub-250ms immediate completions.
- The test mutates `cli->session->pid` in place; later code must reset or understand PID ownership.
- Canceled requests are still received, so changes must not free request objects prematurely.

## Test Signals
Signals include exact NT statuses, elapsed-time checks for delayed and immediate operations, harmless duplicate cancel behavior, and successful cleanup after `smb_raw_exit()`.
