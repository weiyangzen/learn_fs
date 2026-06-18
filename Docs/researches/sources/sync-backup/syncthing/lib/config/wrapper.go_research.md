# sources/sync-backup/syncthing/lib/config/wrapper.go

## sources/sync-backup/syncthing/lib/config/wrapper.go

Purpose: Provides the concurrency-safe service wrapper around `Configuration`, including queued modifications, verifier/committer notification, delayed persistence, accessors, and restart-required tracking.

Important APIs/types/functions: Interfaces `Committer`, `Verifier`, `Waiter`, `Wrapper`, and `ModifyFunction`; concrete `wrapper`, `modifyEntry`, and `modifyResult`; constructors `Wrap` and `Load`; service method `Serve`; mutation methods `Modify`, `RemoveFolder`, `RemoveDevice`; accessors for raw config, GUI, LDAP, options, defaults, folders, devices, ignored state; subscription methods; `Save`; and `RequiresRestart`.

Control flow and state: `Modify` enqueues a function into a bounded channel and waits for immediate validation result. `Serve` serializes queued modifications, applies the function to a deep copy, compares with current config, prepares/verifies/replaces under lock, schedules delayed saves at `minSaveInterval`, and waits for all subscriber committers before processing the next modification. Verifiers can reject before state changes; committers run after state replacement and can set `requiresRestart` by returning false. `Save` writes XML atomically and logs `events.ConfigSaved`.

Dependencies and integration: Uses `suture.Service`, `events.Logger`, `osutil.CreateAtomic`, `LineEndingsWriter`, `protocol`, `sliceutil`, logging, mutexes, atomics, and wait groups. Other packages subscribe as committers to react to config changes; API/UI code uses wrapper modification and accessors.

Risks and test signals: Deadlocks are possible if committers call back into wrapper while locks are held, so waiting is done outside locks where needed. Queue overflow returns `errTooManyModifications`. Delayed save means config state can be in memory before disk persistence. Tests cover commit/validation/restart semantics and save/load round trips.
