# sources/user-network-fs/samba/source4/torture/raw/lockbench.c

## Purpose
`lockbench.c` implements `torture_bench_lock()`, an asynchronous SMB1 byte-range lock benchmark. It opens multiple client connections to a shared file, continuously alternates lock and unlock requests over a small offset ring, reports per-client throughput, and attempts to reconnect when a server connection is lost.

## Important APIs, Types, and Functions
- `struct benchlock_state` stores each client lane: torture context, event loop, tree, fnum, stage, offsets, operation counters, reconnect metadata, outstanding request, and reconnect timer.
- `enum lock_stage` drives the sequence `LOCK_INITIAL`, `LOCK_LOCK`, and `LOCK_UNLOCK`.
- `lock_send()` builds a `RAW_LOCK_LOCKX` request with `LOCKING_ANDX_LARGE_FILES` and sends it using `smb_raw_lock_send()`.
- `lock_completion()` consumes replies, advances the stage, counts operations, and schedules reconnects on EOF/local disconnect/connection reset.
- `reopen_connection()`, `reopen_connection_complete()`, and `reopen_file()` rebuild a lost tree connection and reopen `\\benchlock\\lock.dat`.
- `report_rate()` prints one-second deltas and sends SMB echo keepalives.

## Control Flow
The benchmark reads `timelimit`, `progress`, `nprocs`, and `initial_locks` settings, opens `nprocs` SMB connections, captures remote address/name metadata for reconnects, creates `\\benchlock`, opens `lock.dat` per connection, optionally seeds high-offset locks, then sends the first async lock per state. The main loop runs `tevent_loop_once()` until the time limit expires or `lock_failed` becomes non-zero. On completion it prints aggregate counts, verifies that no lane is severely under-balanced, exits sessions, deletes the test directory, and frees memory.

## State and Persistence Behavior
All benchmark state is in process-global counters (`nprocs`, `lock_failed`, `num_connected`) and per-client `benchlock_state` arrays. The only server-side persistence is the temporary benchmark directory and file plus byte-range locks, which are released by session exit and directory deletion.

## Dependencies and Integration Points
The file uses raw SMB locking, composite async connect APIs, `tevent`, command-line credentials, resolver and loadparm configuration, `smbXcli_conn_remote_sockaddr`, and torture connection helpers. It is a benchmark entry point exposed by `torture/raw/proto.h`, not a suite registration file.

## Risks and Edge Cases
- Reconnect logic assumes the share and remote endpoint are recoverable from the original connection index and captured socket address.
- `lock_send()` increments `lock_failed` if request allocation fails but then dereferences `state->req`; that path would be unsafe if allocation actually returned `NULL`.
- Global counters make concurrent benchmark instances in one process unsafe.
- The printed total ops/second uses `total` without accumulating it from state counts, so the headline rate can be misleading even though per-client counts are printed.
- Timing and balance checks may be noisy on slow servers or during failover.

## Test Signals
Useful signals are the per-client one-second operation deltas, `lock_failed`, reconnect debug messages, final per-client operation counts, and the unbalanced-locking failure when the minimum lane count is below half of the average.
