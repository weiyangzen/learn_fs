# sources/sync-backup/kopia/internal/server/server.go

Purpose: core HTTP API server implementation for Kopia, coordinating authentication, CSRF protection, request dispatch, repository lifecycle, source managers, mounts, tasks, maintenance, static UI serving, scheduler integration, and notifications.

Important APIs/types/functions: `Server`, `Options`, handler registration methods, `isAuthenticated`, auth cookie helpers, `requireAuth`, request wrapper helpers, `Refresh`, `SetRepository`, source-manager synchronization, `ServeStaticFiles`, `InitRepositoryAsync`, `RetryInitRepository`, `runSnapshotTask`, `runMaintenanceTask`, scheduler item generation, and `New`.

Control flow: setup methods register UI and control endpoints with appropriate auth/CSRF wrappers. Requests are authenticated, optionally checked for CSRF, body-read before handler execution, authorized by UI/control role, run under a context detached from request cancellation, and serialized as JSON or API errors. Repository changes stop old schedulers, unmount mounts, stop source managers, close repositories, start maintenance, sync sources, and start scheduler. Scheduler items trigger refresh, maintenance, and local-source snapshots.

State and persistence behavior: server holds repository pointer, source manager map, mount controller map, task manager, maintenance manager, scheduler, auth signing key, init task ID, and snapshot concurrency counters. It persists repository/config changes only through delegated APIs and writes task logs when persistent logs are enabled.

Dependencies and integration points: central integration point for `auth`, `repo`, `snapshot`, `policy`, `mount`, `scheduler`, `uitask`, notification, maintenance, and Gorilla mux.

Risks and test signals: lock ordering, async task startup, CSRF/session cookie generation, repository replacement cleanup, and snapshot concurrency are critical. Tests in this subset cover many API surfaces and authz checks; broader server tests should include shutdown, scheduler refresh, mount cleanup, and concurrent repository reconnects.
