## sources/sync-backup/syncthing/lib/model/service_map_test.go

Purpose: verifies lifecycle semantics of `serviceMap` with dummy suture services and a real supervisor.

Important tests and helpers: `TestServiceMap` has subtests for simple add/remove, overwrite implying removal of the previous service, and `Each` with `RemoveAndWait` during iteration. `dummyService` closes `started` and `stopped` channels around a context wait, giving deterministic lifecycle observations.

Control flow and state: the test starts one outer supervisor, adds a `serviceMap`, then manipulates dummy services under it. It waits on service channels to prove supervisor start/stop propagation. The iteration test removes keys prefixed with `remove` while retaining `keep` services.

Dependencies and integration points: uses `events.NoopLogger` and `suture.NewSimple`. It validates that service-map mutation is compatible with suture tokens and callback-driven iteration.

Risks: subtests call `t.Parallel` while sharing the outer supervisor. The tested `serviceMap` is not concurrent-safe, but each instance is local to a subtest; the shared supervisor must tolerate concurrent additions. No timeout guards around channel waits, so a lifecycle regression can hang until the global test timeout.

Test signals: strong coverage for the documented semantics of replacement, deletion, and iteration mutation.
