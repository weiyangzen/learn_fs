# sources/sync-backup/syncthing/cmd/stdiscosrv/stats.go

Purpose: defines Prometheus metrics for discovery server API, replication, database operations, database writes, and adaptive retry delays.

Important APIs/state: counters/summaries/gauges include `apiRequestsTotal`, `apiRequestsSeconds`, `lookupRequestsTotal`, `announceRequestsTotal`, `replicationSendsTotal`, `replicationRecvsTotal`, `databaseKeys`, `databaseStatisticsSeconds`, `databaseOperations`, `databaseOperationSeconds`, `databaseWriteSeconds`, `databaseLastWritten`, and `retryAfterLevel`.

Control flow: `init` registers all collectors and prewarms key labels for common API, lookup, announcement, and replication results.

State and persistence: metrics are process-local. Database and API code update these collectors as side effects of requests, flushes, expiry, and replication.

Dependencies/integration: depends on Prometheus and standard HTTP method constants. Used by `apisrv.go`, `database.go`, and `amqp.go`.

Risks and test signals: prewarmed label sets improve dashboard continuity, but some error label values used in code are not prewarmed. No direct tests validate metric names or registration.
