
# sources/sync-backup/restic/internal/repository/lock_file_windows.go

Purpose: provides Windows-specific process-liveness support for stale lock detection. Unlike Unix, it does not signal the process; it only attempts `os.FindProcess` and releases the handle.

`lockHandle.processExists` returns false if `FindProcess` fails and true otherwise, logging release errors but not using them as nonexistence. This is intentionally weaker than Unix probing because Windows process signaling semantics differ.

State and persistence behavior are limited to OS process inspection; repository lock state is owned by `lock_file.go`. Integration points are `lockHandle.stale`, the `os` package, and debug logging. Risks include Windows `FindProcess` reporting success for processes that have already exited or for PID reuse, causing stale locks to linger until timestamp expiry. The behavior is indirectly validated by stale-lock tests where build tags select the platform implementation.
