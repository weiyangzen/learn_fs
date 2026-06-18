# sources/object-store/rustfs/crates/protocols/src/sftp/wedge_watchdog.rs

## Purpose
`wedge_watchdog.rs` is the Linux per-session liveness watchdog. It detects sessions silent at the SFTP handler layer while the kernel reports `CLOSE_WAIT`, then cancels the session and shuts down a duplicated socket to unblock russh internals.

## Important APIs, Types, and Functions
`dup_socket` safely duplicates the accepted `TcpStream` fd through `AsFd`. `spawn_for_session` starts the watchdog task. `WedgeReason` records cancellation reasons: close-wait confirmed, probe-failed confirmed, or fallback silence. `Decision` and `evaluate` isolate the state machine. `silence_secs` reads `SessionDiag`.

## Control Flow
The task ticks every `WEDGE_WATCHDOG_TICK_SECS`, skips the immediate first tick, and evaluates silence plus `probe_tcp_state`. Silence below the fast threshold is quiet. Silence above fast threshold with `CloseWait` or probe failure is suspicious on first tick and cancels on a second consecutive signal. `Established` and other known states clear suspicion. Silence above `WEDGE_FALLBACK_KILL_SILENCE_SECS` cancels regardless of probe. On exit, the duplicated socket is shut down with `Shutdown::Both`.

## State and Persistence Behavior
The watchdog keeps only `wedge_suspected` between ticks. It reads diagnostics and cancels the token; dropping the running session drops `SftpDriver`, releasing read caches and triggering multipart cleanup.

## Dependencies and Integration Points
It depends on liveness constants, `lifecycle::probe_tcp_state`, `TcpState`, `socket2`, Linux fd traits, Tokio timers, and `CancellationToken`. `server.rs` spawns it only under `cfg(target_os = "linux")`.

## Risks and Test Signals
Risks include false positives from probe failures, failure to unblock russh without socket shutdown, and noisy cancellation of healthy idle sessions. Tests cover quiet paths, established/transient states, first/second close-wait ticks, probe-failure confirmation, cancel reason selection, fallback silence, and reason strings.
