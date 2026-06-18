# sources/user-network-fs/samba/source4/torture/smb2/lock.c

## Purpose
`lock.c` is the SMB2 byte-range locking torture suite. It validates protocol parameter checking, shared/exclusive lock interaction, pending asynchronous locks, cancellation semantics, zero-byte lock behavior, multi-element atomicity, replay detection, and historical deadlock regressions.

## Important APIs, Types, and Functions
The suite entry point is `torture_smb2_lock_init()`, which registers one- and two-tree tests. The file uses `struct smb2_lock`, `struct smb2_lock_element`, `struct smb2_request`, `struct smb2_create`, `struct smb2_read`, and `struct smb2_write`. Helper macros `CHECK_STATUS`, `CHECK_STATUS_CMT`, `CHECK_STATUS_CONT`, `CHECK_VALUE`, and `WAIT_FOR_ASYNC_RESPONSE` keep assertions concise and event-loop aware.

Key tests include `test_valid_request()` for malformed counts, flags, invalid handles, and range overflow; `test_lock_read_write()` plus `rw-none/shared/exclusive` wrappers for read/write access under locks; `test_lock()`, `test_stacking()`, `test_contend()`, `test_context()`, `test_range()`, and `test_overlap()` for range conflict semantics; `test_async()`, `test_cancel()`, `test_cancel_tdis()`, and `test_cancel_logoff()` for pending lock completion and teardown; `test_zerobytelength()` and `test_zerobyteread()` for zero-length edge cases; `test_unlock()` and `test_multiple_unlock()` for unlock validation and partial multi-lock behavior; `test_truncate()` for overwrite/supersede with held locks; replay tests for resilient/durable/multichannel lock sequence verification; and CTDB/open-vs-brlock deadlock regressions.

## Control Flow
Most tests create `testlock`, create one or more handles to a test file, write a small buffer, issue SMB2 LOCK operations with exact offsets/lengths/flags, and assert returned NTSTATUS values. Async tests issue `smb2_lock_send()`, drive `tevent` until the request is cancellable/pending, then cancel, close, disconnect, log off, or unlock the blocking range before receiving the pending response. Replay tests set specific lock sequence bucket/sequence values and verify whether repeated requests are ignored or treated as new requests according to dialect, resiliency, durable handle, and multichannel capabilities. Deadlock regressions run either a simple lock/unlock relock sequence on CTDB or two continuous async loops, one opening/closing a file and one locking/unlocking another file until a configured timer stops.

## State and Persistence Behavior
The file creates transient files and directories under `testlock` and removes them with `smb2_deltree()`. Lock state lives on the server under open handles and is intentionally exercised across multiple handles, sessions, trees, and teardown events. No local durable state is written, but replay tests intentionally depend on server-side per-open lock sequence buckets, resilient handle state via `FSCTL_LMR_REQ_RESILIENCY`, durable-open state, and multichannel capabilities.

## Dependencies and Integration Points
The suite depends on Samba SMB2 client calls, `smbXcli_conn_protocol()`/capability helpers, `tevent`, torture settings, cluster configuration via `lpcfg_clustering()`, and utility helpers such as `torture_smb2_testfile()`, `torture_smb2_testdir()`, `smb2_util_write()`, and `smb2_util_close()`. The two-tree `overlap` and `open-brlock-deadlock` cases integrate cross-session behavior into the same suite.

## Risks and Edge Cases
The suite encodes target-specific behavior for Windows Server 2008 quirks (`w2k8`) and optional invalid-range support, so configuration mismatches can turn expected failures into false alarms. Several tests intentionally tolerate alternate teardown statuses because servers close file, tree, and session state in different orders. Long-running range and deadlock tests depend on `torture_numops` or an opt-in timeout and can be expensive. The misspelled option `open_brlock_deadlock_timemout` is part of the tested interface in this file.

## Test Signals
The registered subtests provide detailed NTSTATUS signals for every major lock path: invalid parameters, lock conflict versus file lock conflict, cancellation, tree/session teardown, zero-byte locking, multi-lock atomicity, lock sequence replay, CTDB tombstone relock, and async open/byte-range lock progress under load.
