# sources/test-tools/syzkaller/dashboard/app/graphs_test.go

Purpose: verifies graph endpoints render with realistic test data and malformed fuzzing metric selectors are rejected.

Important APIs/types/functions: `TestManagersGraphs`, `managersGraphFixture`, `TestManagersGraph_FuzzingMetric_OK_OnValidInput`, and `TestManagersGraph_FuzzingMetric_BadRequest_OnMalformedInput`.

Control flow: tests upload builds, manager stats, and crashes, advance mocked time, drain reporting email, and issue authenticated GETs to graph routes. Metric tests call the fuzzing graph with valid and injection-like malformed `Metrics` form values.

State/persistence: uses the test datastore through `NewCtx`; manager stats, bugs, and crash history are persisted before graph handlers query them.

Dependencies/integration: integrates API upload, reporting cron/email flow, auth helpers, graph handlers, and bad-request handling.

Risks/test signals: most endpoint checks do not assert graph content; strongest signal is malformed metric rejection to keep unknown values away from `extractMetric`.
