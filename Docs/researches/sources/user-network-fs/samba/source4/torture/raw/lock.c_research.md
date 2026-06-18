# sources/user-network-fs/samba/source4/torture/raw/lock.c

## Purpose
`lock.c` defines the `RAW-LOCK` smb-torture suite for SMB1 byte-range locking semantics. It probes legacy `SMBlock`/`SMBunlock`, `LOCKING_ANDX`, lock cancellation, status-code caching, zero-byte lock behavior, unlock ordering, shared/exclusive stacking, zero-byte reads against locked ranges, and multi-range blocking queue precedence. The tests are protocol conformance checks rather than reusable production logic.

## Important APIs, Types, and Functions
- Uses Samba raw client primitives from `libcli/raw`: `smb_raw_lock`, `smb_raw_lock_send`, `smbcli_request_simple_recv`, `smb_raw_open`, `smb_raw_exit`, `smb_raw_ulogoff`, `smb_tree_disconnect`, `smb_raw_tcon`, and raw read helpers.
- Uses high-level torture helpers: `torture_suite_create`, `torture_suite_add_1smb_test`, `torture_setup_dir`, `torture_assert*`, `torture_result`, `torture_comment`, and target feature settings such as `samba3`, `smbexit_pdu_support`, and `range_not_locked_on_file_close`.
- Main test functions are `test_lock`, `test_lockx`, `test_pidhigh`, `test_async`, `test_errorcode`, `test_changetype`, `test_zerobytelocks`, `test_unlock`, `test_multiple_unlock`, `test_stacking`, `test_zerobyteread`, and `test_multilock` through `test_multilock6`.
- `struct double_lock_test` and `zero_byte_tests[]` encode the zero-byte lock overlap matrix.
- `torture_raw_lock()` registers all subtests in the `lock` suite.

## Control Flow
Each subtest creates `\\testlock`, opens one or more files, builds a `union smb_lock` with `struct smb_lock_entry` ranges, performs raw synchronous or asynchronous locking operations, validates exact NT status results, and tears down with `smb_raw_exit()` plus `smbcli_deltree()`. The async tests send pending lock requests with timeouts, then cancel by explicit `LOCKING_ANDX_CANCEL_LOCK`, unlock, file close, `SMBexit`, user logoff, or tree disconnect and assert that pending requests complete immediately with Windows-compatible statuses.

The `test_errorcode` path is the densest status-code test. It opens two fnums for the same file, demonstrates per-handle error-code cache behavior for `NT_STATUS_LOCK_NOT_GRANTED` versus `NT_STATUS_FILE_LOCK_CONFLICT`, repeats the matrix with `timeout = 0` and `timeout > 0`, and checks that pending timed locks only update the cache when the error is reported to the client.

The multi-lock tests encode queue ordering rules. `test_multilock` checks that a two-range blocked lock completes only after both original ranges are unlocked. `test_multilock2` through `test_multilock6` vary shared/exclusive modes and independent ranges to prove that pending requests have precedence by arrival order while unrelated ranges can proceed.

## State and Persistence Behavior
The tests create transient files below `\\testlock`; no persistent configuration is written. State is held in local `union smb_lock`, `struct smb_lock_entry`, fnum, pid, request, and tree/session objects. Several tests deliberately mutate `cli->session->pid` or lock-entry `pid` to validate server PID semantics. Cleanup relies on `smb_raw_exit()` to release locks and `smbcli_deltree()` to delete the test directory.

## Dependencies and Integration Points
This file integrates with the Samba4 torture runner through `torture_raw_lock()`. It depends on SMB1 raw client behavior, the torture context settings system, command-line credentials for secondary session setup, and server support for old SMB PDUs. It uses `lpcfg_smbcli_session_options`, `smb_composite_sesssetup`, and `RAW_TCON_TCONX` to create additional sessions/tree connects inside cancellation tests.

## Risks and Edge Cases
- Many assertions depend on server-specific compatibility switches. Incorrect target settings can turn expected Windows/Samba divergences into false failures.
- Async tests are timing-sensitive and use two-second immediacy checks; slow virtualized or remote environments may cause flakes.
- Tests intentionally leave requests pending while manipulating session/tree state, so cleanup regressions can leak locks until connection teardown.
- The multi-lock cases protect subtle lock queue semantics; simplifying them risks losing coverage for deadlock, starvation, or wrong ordering bugs.
- `CHECK_STATUS` macros jump to common cleanup labels; changes must keep fnums initialized before cleanup paths.

## Test Signals
Primary pass/fail signals are exact NT status matches, immediate completion timing checks, request state checks such as `req->state <= SMBCLI_REQUEST_RECV`, successful zero-byte read counts, and successful cleanup of the test tree. Suite registration names are `lockx`, `lock`, `pidhigh`, `async`, `errorcode`, `changetype`, `stacking`, `unlock`, `multiple_unlock`, `zerobytelocks`, `zerobyteread`, and `multilock*`.
