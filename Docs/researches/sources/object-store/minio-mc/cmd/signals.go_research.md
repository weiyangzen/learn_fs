# sources/object-store/minio-mc/cmd/signals.go

## Purpose
Centralizes OS signal handling for the CLI by canceling global context, stopping profiling, and exiting with signal-specific status codes.

## Important APIs, types, and functions
- `trapSignals(sig ...os.Signal)` registers for supplied signals, waits for one signal, optionally cancels global state, and exits.

## Control flow
The function creates a buffered signal channel, registers it with `signal.Notify`, blocks until a signal arrives, stops notifications, and checks `GlobalTrapSignals`. If trapping is disabled it returns, allowing caller-specific handling. Otherwise it calls `stopProfiling`, cancels `globalContext` via `globalCancel`, maps signal string to global exit status, and calls `os.Exit`.

## State and persistence
Mutates process state only: signal registration, profiling lifecycle, global context cancellation, and process exit. No file or remote persistence.

## Dependencies and integration points
Integrates with global context variables, profiling cleanup, and global exit status constants. Uses Go `os` and `os/signal`.

## Risks and edge cases
- The signal channel is closed by defer after `signal.Stop`, which is safe for this local channel but can be risky if external senders existed.
- It relies on `s.String()` values like `interrupt`, `killed`, and `terminated`.
- `SIGKILL` cannot actually be trapped on Unix, so the `killed` branch is mostly defensive.

## Test signals
No direct tests. Testing would require process-level signal handling or factoring signal-to-exit-code mapping.
