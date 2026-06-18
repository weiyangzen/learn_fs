# sources/sync-backup/syncthing/lib/semaphore/semaphore.go

Purpose: implements a byte-counting semaphore with adjustable capacity and a `MultiSemaphore` composition helper.

Important APIs and control flow: `New` clamps negative capacity to zero and initializes `available == max`. `Take` and `TakeWithContext` acquire up to `max` bytes; oversized takes are clamped. `TakeWithContext` runs the blocking acquisition in a goroutine, broadcasts on cancellation, then waits for the inner path to observe the context. `Give` clamps returned size and caps availability at `max`. `SetCapacity` changes `max`, shifts `available` by the capacity diff, clamps into `[0,max]`, and broadcasts. `Available` returns a locked snapshot. `MultiSemaphore` takes semaphores in slice order and gives them back in reverse order, skipping nil entries.

State and persistence: all state is in-memory `max`, `available`, mutex, and condition variable. No persistence.

Dependencies and integration: used wherever Syncthing needs shared throughput or resource limits. `context` support allows cancellation-friendly startup/shutdown paths.

Risks: `MultiSemaphore.TakeWithContext` does not roll back earlier acquisitions if a later semaphore returns context error, so callers must use it where cancellation semantics tolerate that or arrange cleanup. `TakeWithContext` spawns a goroutine per call. Test coverage focuses on capacity mutation and clamping.
