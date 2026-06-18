# sources/test-tools/syzkaller/dashboard/app/index.yaml

Purpose: App Engine datastore composite index definitions required by dashboard queries.

Important indexes: `Bug` indexes for namespace/status, happened-on, commits, title/sequence, merged/alternate titles, closed state, commit-info polling, bisection candidates, subsystem refresh, labels, fix candidates, and AI workflow fields; `Build` indexes for manager/type/time and asset scans; ancestor `Crash` indexes for repro/report/priority ordering; `Job` indexes for pending/completed/history queries; `Discussion` and `ReproTask` indexes for message and repro queues.

Control flow: none executable; it must match datastore query filter/order shapes in Go code.

State/persistence: controls datastore-maintained query acceleration structures, not entity schema.

Dependencies/integration: coupled to queries in entity, job, reporting, asset, subsystem, AI, discussion, and UI code.

Risks/test signals: query/index drift can break production even if local tests pass; repeated-property composite indexes have write amplification. Deployment/index validation is the key signal.
