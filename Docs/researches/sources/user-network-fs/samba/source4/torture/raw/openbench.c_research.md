# sources/user-network-fs/samba/source4/torture/raw/openbench.c

## Purpose
This file implements `torture_bench_open()`, an asynchronous benchmark for SMB `NTCREATEX` open/close throughput. It opens multiple client connections, repeatedly cycles through a shared pool of filenames, keeps one current open per worker, asynchronously closes the previous handle after each successful open, and reports per-worker and aggregate operations per second. It is both a performance benchmark and a stress test for share-mode contention, reconnect handling, and event-loop-driven raw SMB request sequencing.

## Important APIs, types, and functions
The central state container is `struct benchopen_state`, which tracks the torture context, event context, client/tree pointers, current and pending fnums, file indices, request pointers, reconnect parameters, counters, retry counts, and timer handles. The key local functions are `next_open()`, `next_close()`, `open_completed()`, `close_completed()`, `reopen_connection()`, `reopen_connection_complete()`, `echo_completion()`, and `report_rate()`. Important APIs include `smb_raw_open_send()`, `smb_raw_open_recv()`, `smb_raw_close_send()`, `smbcli_request_simple_recv()`, `smb_composite_connect_send()`, `smb_composite_connect_recv()`, `smb_raw_echo_send()`, `tevent_add_timer()`, `tevent_loop_once()`, and `torture_open_connection_ev()`.

## Control flow
`torture_bench_open()` reads settings (`timelimit`, `nprocs`, `progress`), allocates one `benchopen_state` per worker, opens the initial SMB connections, records remote address and called-name data for later reconnects, prepares `\benchopen`, and builds `3 * nprocs` filenames. Each worker starts at file index zero and calls `next_open()`.

`next_open()` increments the worker operation count, advances the circular file index, fills an `RAW_OPEN_NTCREATEX` request with `SEC_RIGHTS_FILE_ALL`, share access zero, and `NTCREATEX_DISP_OVERWRITE_IF`, then sends it asynchronously. `open_completed()` receives the response. Disconnect-like statuses free the old tree/client, decrement `num_connected`, and schedule a one-second reconnect. Sharing violations are retried immediately and counted. Successful opens rotate the newly opened fnum into `open_fnum`, move the old open fnum into `close_fnum`, optionally starts `next_close()`, and immediately schedules another open to keep pressure on the server.

`next_close()` sends an async raw close for the previous fnum. `close_completed()` handles disconnect-like statuses similarly to open completion and increments a global close-failure counter on other errors. `report_rate()` prints per-worker delta counts once per second and sends async SMB echo requests on live connections so idle paths remain active, especially during IP takeover scenarios. After the time limit, the benchmark cancels the report timer, prints per-worker counts and retries, checks that the slowest worker is not less than half the average, exits sessions, removes `\benchopen`, and frees benchmark memory.

## State and persistence
Global state includes `nprocs`, `open_failed`, `close_failed`, `fnames`, `num_connected`, and `report_te`. Per-worker state is talloc-owned under the benchmark context. Server-side state consists of the `\benchopen` directory, a rotating set of `fileN.dat` files, open handles, share-mode conflicts, and live SMB connections. Cleanup removes `\benchopen` on the success path; failure paths free the talloc context but may leave server-side files if the benchmark aborts early.

## Dependencies and integration points
The benchmark sits in the raw torture layer but uses several broader Samba facilities: command-line credentials, `lpcfg_*` client/session/gensec options, resolver context, composite SMB connect APIs, SMB echo keepalive, socket-address formatting, and `smbXcli_conn_*` accessors. It expects the torture harness to provide an event loop and indexed connection settings through `torture_get_conn_index()` and `torture_open_connection_ev()`.

## Risks
This code intentionally runs indefinitely until the configured time limit and can generate heavy open/close contention. The global failure counters are not reset inside the function, so repeated in-process invocations could inherit failure state. In `next_open()`, the returned request is assumed non-NULL before assigning callback fields. Reconnect paths mix talloc ownership of `tree` and `cli`; freeing one while callbacks are outstanding would be risky if future code changes allowed overlapping reconnect and request completion. Failure exits do not run full server cleanup. The balance check is a benchmark heuristic and can fail on real scheduling imbalance rather than protocol malfunction.

## Test signals
Useful signals are `open_failed` or `close_failed`, unexpectedly high `open_retries`, reconnect churn, unbalanced worker operation counts, low aggregate ops/sec, failure to create or clean `\benchopen`, and disconnect-like status handling (`NT_STATUS_END_OF_FILE`, `NT_STATUS_LOCAL_DISCONNECT`, `NT_STATUS_CONNECTION_RESET`) during open, close, or echo completion.
