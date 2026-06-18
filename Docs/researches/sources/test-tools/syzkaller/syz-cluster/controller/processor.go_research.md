# sources/test-tools/syzkaller/syz-cluster/controller/processor.go

Purpose: schedules and tracks workflow sessions for uploaded series in syz-cluster.

Important APIs/types/functions: `SeriesProcessor`, `NewSeriesProcessor`, `Loop`, `streamSeries`, `seriesRunner`, `handleSession`, `stopRunningTests`, and `updateSessionLog`.

Control flow: `Loop` starts a runner, requeues previously running sessions, then streams waiting sessions from DB. `streamSeries` polls DB when queue has capacity, marks sessions started before enqueueing. `seriesRunner` limits concurrent workflows. `handleSession` polls workflow status, starts missing workflows, writes logs to blob storage, marks sessions finished, and stops still-running tests. `stopRunningTests` converts orphaned running test steps to error.

State and persistence: session/session-test/series state is in Spanner repositories; logs are written to blob storage and referenced by `LogURI`.

Dependencies and integration points: integrates app environment, DB repositories, blob storage, and Argo workflow service.

Risks: comment notes no sane deadline yet, so running workflows can be tracked indefinitely. Single-controller assumption avoids duplicate starts; DB `Start` handling mitigates restart races.

Test signals: `processor_test.go` covers normal processing, restart recovery, and stuck running test cleanup.
