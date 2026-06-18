# sources/sync-backup/syncthing/internal/timeutil/timeutil.go

Purpose: Provides strictly increasing unix-nanosecond timestamps independent of wall-clock resolution or backward jumps.

Important APIs/types/functions: `StrictlyMonotonicNanos` loops on an atomic `prevNanos`, computes `max(time.Now().UnixNano(), old+1)`, and commits with compare-and-swap.

Control flow: The function retries until its CAS succeeds, guaranteeing each caller observes a value greater than the last committed value.

State and persistence behavior: Maintains process-global atomic timestamp state. No disk persistence.

Dependencies and integration points: Depends on `sync/atomic` and `time`. Useful where database keys, event timestamps, or token expiries need monotonic nanosecond ordering.

Risks: If the process emits many timestamps while wall time moves backward, returned values can run ahead of real time. It is process-local only and does not coordinate across restarts or nodes.

Test signals: No direct test in this subset. Concurrency and clock-backward tests would be valuable.
