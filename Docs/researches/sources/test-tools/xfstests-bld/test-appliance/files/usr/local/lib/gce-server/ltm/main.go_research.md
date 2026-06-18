# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/main.go

Purpose: HTTPS entrypoint for the Lightweight Test Manager.

Important endpoints: `/gce-xfstests` accepts authenticated user requests; `/internal` accepts KCS callbacks; `/status` returns LTM local state plus KCS bisector status. `runTests` parses requests, assigns a timestamp or user-provided test ID, routes unwatch/watch/bisect/build requests to watcher or KCS forwarding, otherwise starts a `ShardScheduler`.

Control flow: user branch watch creates `GitWatcher`; bisect and commit build create `InternalOptions` and `ForwardKCS`; plain tests call `NewShardScheduler` and `Run` in a goroutine; mock mode uses `MockNewShardScheduler`. `status` calls `server.InternalQuery` to merge KCS status with `SharderStatus` and `WatcherStatus`.

State and dependencies: uses `sharderMap`, `watcherMap`, KCS internal HTTPS, GCE config, and log directories. Authentication and panic wrapping come from the shared server package.

Risks and test signals: asynchronous launch means HTTP success only means work was accepted. Request classification relies on option combinations. Tests should cover each route, authentication boundaries, and status aggregation when KCS is absent.
