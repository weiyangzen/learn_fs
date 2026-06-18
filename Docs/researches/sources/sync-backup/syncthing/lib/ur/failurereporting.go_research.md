# sources/sync-backup/syncthing/lib/ur/failurereporting.go

Purpose: aggregates and sends failure reports when crash/failure reporting is enabled through configuration.

Important APIs and control flow: `FailureDataWithGoroutines` captures goroutine profiles into `contract.FailureData`. `NewFailureHandler` returns a Suture service and config committer. `Serve` subscribes to config changes, applies options to subscribe/unsubscribe from `events.Failure`, buffers failures by description with first/last/count, flushes reports once failures age past `minDelay` or accumulate beyond `maxDelay`, sends asynchronously, and on shutdown sends remaining reports with a shorter final timeout. `applyOpts` computes `CRURL + "/failure"` and subscribes when usage reporting is accepted. `CommitConfiguration` pushes changed CR options into `optsChan`. `sendFailureReports` JSON-encodes an array and POSTs with Syncthing dialer and TLS defaults.

State and persistence: in-memory aggregation map; remote HTTP POST side effects. No local persistence.

Dependencies and integration: started early in `App.startup`; depends on events, config, suture, TLS/dialer, and usage contract.

Risks: `CommitConfiguration` sends on an unbuffered channel and can block if service is not receiving. Enabling logic checks `URAccepted > 0`, not `CREnabled`, despite commit watching `CREnabled`. Network failures only warn and drop reports.
