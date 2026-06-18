
# sources/user-network-fs/samba/source4/torture/nbench/nbio.c

## Purpose
`nbio.c` implements the SMB operation layer, handle/lock tracking, shared benchmark accounting, reconnect restoration, and timer-driven statistics for the nbench torture test. It translates replayed NetBench operations into Samba raw SMB calls and validates each response against the expected NTSTATUS from the load file.

## Important APIs, Types, And Functions
Persistent in-process structures are `struct lock_info`, `struct createx_params`, and `struct ftable`. `ftable` maps load-file handles to server FIDs and records create parameters plus active byte-range locks so reconnect can reopen and relock files. The shared-memory `children` array tracks each process's bytes, warmup bytes, current line, done flag, connected flag, max latency, and start time. Setup/accounting APIs include `nbio_shmem()`, `nb_setup()`, `nbio_time_reset()`, `nbio_time_delay()`, `nbio_target_rate()`, `nbio_result()`, `nbio_latency()`, `nb_tick()`, `nb_alarm()`, and `nb_exit()`. Recovery APIs include `nb_reconnect()`, `nb_reopen_all_files()`, and `nb_reestablish_locks()`. Operation APIs include `nb_createx()`, `nb_close()`, `nb_unlink()`, `nb_rename()`, `nb_deltree()`, `nb_rmdir()`, `nb_mkdir()`, `nb_qpathinfo()`, `nb_qfileinfo()`, `nb_qfsinfo()`, `nb_sfileinfo()`, `nb_findfirst()`, `nb_writex()`, `nb_write()`, `nb_readx()`, `nb_lockx()`, `nb_unlockx()`, `nb_flush()`, and `nb_sleep()`.

## Control Flow
`nbio_shmem()` allocates anonymous shared memory for child statistics and initializes the benchmark timer. `nb_setup()` sets the process's `nbio_id`, stores the current `smbcli_state` in the static `c`, installs an oplock break handler, and marks the child connected. Operation wrappers look up file handles with `find_handle()`, build the corresponding `union smb_*` raw request, call a `smb_raw_*` function, and pass results to `check_status()`. Successful creates add or update `ftable`; closes remove entries; locks add `lock_info`; unlocks remove matching lock state. If a reconnect occurs, `nb_reconnect()` frees the old client, opens a new connection, calls `nb_setup()`, then replays create and lock state from `ftable`.

## State And Persistence
Most state is runtime memory, split between per-process globals and anonymous shared memory visible to all nbench children. Remote persistent state consists of files, directories, locks, and open handles on the SMB server. `nb_deltree()` sends an SMB exit, clears local handle state, recursively deletes a server tree, and removes the directory. Timers separate warmup bytes from measured bytes and mark all children done after the configured execution window.

## Dependencies
The file depends on Samba raw SMB client APIs, torture connection helpers, talloc, anonymous shared memory, timeval helpers, signal/alarm behavior, linked-list macros from `dlinklist.h`, and `nbench_line_count` from `nbench.c`. It also relies on the server honoring SMB open, read, write, lock, search, metadata, flush, tree cleanup, and oplock acknowledgement semantics.

## Integration Points
`nbench.c` dispatches all replayed operations into these APIs. `nb_alarm()` is installed as a `SIGALRM` handler by `torture_nbench()` and periodically prints connection count, lines per process, throughput, phase, and latency. The oplock handler integrates with the SMB transport to acknowledge break-to-none requests. Reconnect behavior integrates with the `NB_RETRY` macro in `nbench.c`.

## Risks
Several wrappers allocate buffers with `malloc(size)` and immediately `memset()` without checking allocation failure. `check_status()` treats some transport-like errors specially by returning false for retry; other expected/unexpected mismatches can exit the process. The static `c`, `nbio_id`, and `ftable` mean the code is not reentrant. `nb_mkdir()` intentionally ignores errors, which is useful for base fileset creation but hides failures. Shared state updates are not protected by locks; the design assumes mostly per-child writes with aggregate reads by the parent signal handler. The file table is talloc-allocated under `NULL` or file entries, so leaks are acceptable for benchmark lifespan but matter during repeated embedded use.

## Test Signals
Signals include exact status validation, fatal handle lookup failures, reconnect logs followed by reopened files and reestablished locks, correct byte accounting for reads/writes, `nb_alarm()` phase transitions from warmup to execute to cleanup, and final throughput calculation excluding warmup bytes. Focused tests should force reconnects with open locked files, exercise create disposition retry rules, validate lock tracking removal, and cover error/status mismatch branches.
