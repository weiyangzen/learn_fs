# sources/sync-backup/syncthing/lib/syncthing/auditservice_test.go

Purpose: verifies audit service subscription timing and shutdown behavior.

Important tests: `TestAuditService` starts an event logger, emits one event before creating the audit service, starts the service with a buffer writer, emits a second event, cancels the audit service, then emits a third event. It asserts the buffer excludes the first and third events and includes the second.

State and persistence: uses an in-memory `bytes.Buffer` and event logger goroutine.

Dependencies and integration: exercises `events.Logger` subscription delivery and audit service `Serve`.

Risks and signals: validates lifecycle behavior but uses sleeps to allow subscription and delivery, making it somewhat timing-sensitive. It does not check JSON validity or writer error handling.
