# sources/user-network-fs/samba/source3/lib/server_id_watch.c

## Purpose
This file implements an asynchronous tevent request that completes when a target `server_id` no longer exists. It is a polling process-death watcher with optional diagnostics for long waits.

## Important APIs, Types, And Functions
`server_id_watch_send()` allocates `server_id_watch_state`, records start/warn timestamps, reads debug options from loadparm, immediately completes if `serverid_exists()` is already false, or schedules a 500 ms `tevent_wakeup`. `server_id_watch_waited()` repeats the liveness check and reschedules until the process is gone. `server_id_watch_recv()` returns any unix error and optionally copies the watched ID.

## Control Flow
The request is callback-driven. Every wakeup frees the subrequest, checks liveness, and either completes the parent request or schedules another wakeup. If debug is enabled and ten seconds elapsed since the last warning, it either runs a configured debug script as root or reads `/proc/<pid>/stack` for local processes with procfs support, then logs the output.

## State And Persistence
State is only in the tevent request. External side effects are debug script execution and log messages; no database is mutated.

## Dependencies And Integration Points
It depends on `serverid_exists()`, tevent, Samba loadparm, root privilege helpers, `smbrun`, `fd_load`, `/proc` stack reading, and server ID formatting. It integrates with code that needs nonblocking wait-for-process-exit semantics.

## Risks And Test Signals
Risks include polling latency, debug script privilege and output handling, procfs availability, clustered ID formatting, and repeated warnings for long-lived targets. Tests should cover already-dead completion, delayed completion, wakeup failure/oom, debug disabled/enabled paths, custom debug script invocation, and local/nonlocal process handling.
