# sources/user-network-fs/samba/source4/torture/raw/offline.c

## Purpose
`offline.c` implements `torture_test_offline()`, a stress benchmark for SMB offline-file handling. It repeatedly performs asynchronous load, save, set-offline-attribute, and get-attribute operations across multiple connections and tracks throughput plus worst latency.

## Important APIs, Types, and Functions
- `enum offline_op` defines `OP_LOADFILE`, `OP_SAVEFILE`, `OP_SETOFFLINE`, and `OP_GETOFFLINE`.
- `struct offline_state` tracks each concurrent operation lane: tree, file number, operation counters, file name, composite request objects, raw request, current op, and start time.
- `filename()` maps an integer to `\\testoffline\\fileN.dat`.
- `loadfile_callback()`, `savefile_callback()`, `setoffline_callback()`, and `getoffline_callback()` validate async completions and resubmit work.
- `test_offline()` chooses a random operation and random file, sends the corresponding composite or raw async request, and records latency.
- `report_rate()` prints ops/sec, online/offline counts, current and worst latencies, and sends echo keepalives.

## Control Flow
The test reads `timelimit`, `progress`, `nprocs`, global `torture_entries`, and global `torture_numops`. It opens `nprocs` connections, creates `numstates = nconnections * torture_entries` lanes, reuses connection trees across lanes, extends SMB request timeout for offline file delays, creates `\\testoffline`, pre-creates `torture_numops` files with deterministic 8 KiB contents, starts one async random operation per lane, and runs the event loop until the time limit expires or a callback marks failure. After the timed run it sets `test_finished`, drains all outstanding requests, prints worst latencies, deletes the tree, and frees memory.

## State and Persistence Behavior
Global counters store connection count, lane count, test failure, finish flag, current latencies, and worst latencies. Each lane stores its outstanding request and counters. Server-side state is the temporary file corpus plus offline attributes; contents are checked against `1 + (file_number % 255)` after each load.

## Dependencies and Integration Points
The file depends on composite SMB helpers `smb_composite_loadfile_send/recv` and `smb_composite_savefile_send/recv`, raw path info and set path info APIs, `tevent`, torture global operation settings, and SMB echo keepalive. It is a benchmark-style torture entry point rather than a suite factory.

## Risks and Edge Cases
- Globals make repeated runs in the same process sensitive unless state is reinitialized by process lifetime.
- `test_failed` is an int but sometimes assigned boolean-style values.
- Offline/HSM systems can legitimately have long latencies; the transport timeout is raised to 200 seconds but the benchmark still depends on event-loop responsiveness.
- Callbacks resubmit recursively until `test_finished`, so any missed completion can stall drain.
- Failed setup paths free memory without deleting `\\testoffline`, leaving cleanup to later runs.

## Test Signals
Signals are callback status failures, data integrity mismatches, online/offline attribute counts, per-second throughput, latency maxima per operation type, echo disconnect failures, and successful final drain of all outstanding load/save/raw requests.
