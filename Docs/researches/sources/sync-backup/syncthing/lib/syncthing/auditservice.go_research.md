# sources/sync-backup/syncthing/lib/syncthing/auditservice.go

Purpose: supervised service that writes all Syncthing events as JSON lines to an audit writer.

Important APIs and control flow: `newAuditService` stores an `io.Writer` and event logger. `Serve` subscribes to `events.AllEvents`, defers unsubscribe, creates a JSON encoder, and loops over subscription events or context cancellation. Each event received is encoded to the writer. If the subscription channel closes unexpectedly, it waits for context cancellation and returns that error. `String` returns a pointer-qualified service name.

State and persistence: state is the active event subscription and destination writer. Persistence depends on the writer supplied by the app.

Dependencies and integration: added during app startup when `Options.AuditWriter` is non-nil. Uses event logger subscription API and Suture service semantics.

Risks: `enc.Encode` errors are ignored, so failed audit writes do not stop the service. It logs only events after subscription starts. Test coverage checks event timing and stop behavior.
