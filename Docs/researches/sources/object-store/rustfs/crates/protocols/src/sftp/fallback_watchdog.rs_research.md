# sources/object-store/rustfs/crates/protocols/src/sftp/fallback_watchdog.rs

## Purpose
`fallback_watchdog.rs` provides the non-Linux liveness backstop for SFTP sessions. Without the Linux `/proc/net/tcp[6]` CLOSE_WAIT probe, it relies only on silence at the SFTP handler layer.

## Important APIs, Types, and Functions
`spawn_for_session(session_diag, cancel_token)` starts the per-session Tokio task. `silence_secs` compares wall-clock time with `SessionDiag.last_activity_ms`. `fallback_threshold_reached` checks `WEDGE_FALLBACK_KILL_SILENCE_SECS`.

## Control Flow
The task runs on `WEDGE_WATCHDOG_TICK_SECS`, delays missed ticks, and skips the immediate first tick. Each tick races against token cancellation. If silence reaches the fallback threshold, it logs a warn event with session id, peer, silence, and reason `fallback_silence`, then cancels the session token and exits. Clean session end or listener shutdown cancels the same token and exits the task.

## State and Persistence Behavior
It holds only an `Arc<SessionDiag>` and a cancellation token clone. The activity stamp is relaxed atomic state updated by auth, subsystem dispatch, and SFTP handlers. Cancellation drops the running session and eventually the driver, releasing handles, read caches, and multipart state.

## Dependencies and Integration Points
It depends on liveness constants, `SessionDiag`, Tokio timers, and `CancellationToken`. `server.rs` spawns it only on non-Linux targets after SSH handshake completion.

## Risks and Test Signals
The tradeoff is coarse detection: long operations that do not stamp activity can be canceled at the fallback threshold. Tests pin threshold boundaries, cancellation under paused time, clean early cancellation releasing the diagnostic `Arc`, and silence calculations from stale stamps.
