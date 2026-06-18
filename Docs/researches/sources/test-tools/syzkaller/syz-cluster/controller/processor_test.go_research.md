# sources/test-tools/syzkaller/syz-cluster/controller/processor_test.go

Purpose: integration-style tests for `SeriesProcessor`.

Important APIs/types/functions: `TestProcessor`, `TestFinishRunningSteps`, `awaitFinishedSessions`, `mockedWorkflows`, `newMockedWorkflows`, and `prepareProcessorTest`.

Control flow: tests create a fake app environment and controller client, run processor loops, upload series/build/session-test data, drive mocked workflow completion through a channel, simulate restart, and wait until sessions are marked finished.

State and persistence: uses test Spanner/blob environment via `app.TestEnvironment`; workflow mock holds in-memory created/finished maps.

Dependencies and integration points: covers controller upload helpers, repositories, workflow service interface, and processor loop concurrency.

Risks: time-based waits can be flaky under severe load, though deadlines are short and poll delay is reduced.

Test signals: strong signal for restart recovery and cleanup of running tests after workflow completion.
