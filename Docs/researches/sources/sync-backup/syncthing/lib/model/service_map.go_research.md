## sources/sync-backup/syncthing/lib/model/service_map.go

Purpose: generic utility that maps arbitrary keys to `suture.Service` instances and manages their lifecycle under an internal supervisor.

Important APIs: `newServiceMap` constructs the map and supervisor with event logging. `Add` replaces any existing service for a key, starts the new service through the supervisor, and stores its token. `Get`, `Stop`, `StopAndWaitChan`, `Remove`, `RemoveAndWait`, `RemoveAndWaitChan`, and `Each` provide keyed lifecycle and iteration operations. `Serve` runs the internal supervisor; `String` identifies the service.

Control flow and state: state is two maps, one from key to service and one from key to supervisor token. `Add` calls `Remove` first to avoid duplicate services. `Stop` removes the service from the supervisor but keeps it in `services`; `Remove` stops and deletes both maps. Wait variants return or consume a single error from supervisor removal. `Each` snapshots keys before iteration so callbacks can mutate the map, including removing current entries.

Dependencies and integration points: built on `github.com/thejerf/suture/v4`, `svcutil.AsService`, and `events.Logger`. It is intended for model-owned folder or device service collections where keyed add/remove must stay paired with supervisor membership.

Risks: explicitly not safe for concurrent use; callers must serialize access. Stopped services remain addressable after `Stop`, which is intentional but can surprise code expecting absence. Misusing wait timeouts can leak asynchronous stop errors if the channel is ignored.

Test signals: `service_map_test.go` covers add/remove startup, replacement stopping the old service, and removal while iterating.
