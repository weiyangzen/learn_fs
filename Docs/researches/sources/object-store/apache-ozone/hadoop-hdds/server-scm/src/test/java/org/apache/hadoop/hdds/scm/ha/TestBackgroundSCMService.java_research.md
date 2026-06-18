<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestBackgroundSCMService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestBackgroundSCMService.java

Purpose: This suite verifies `BackgroundSCMService` lifecycle and run gating based on SCM safe mode and a post-safe-mode delay.

Important APIs and types: It uses `BackgroundSCMService.Builder`, `SCMContext`, `TestClock`, `PipelineManager.scrubPipelines`, `SafeModeStatus`, and Mockito timeout verification.

Control flow: Setup creates a service with 1 ms interval/wait values and a periodical task that calls a mocked pipeline manager. `testStop` confirms running state toggles off. `testNotifyStatusChanged` starts paused, exits safe mode but remains delayed, advances the test clock by 60 seconds to permit running, then re-enters safe mode and pauses. `testRun` manually notifies, advances time, calls `runImmediately`, and verifies the task executes.

State and persistence behavior: Runtime state includes service running flag, service status, SCM safe-mode status, and injected clock time. No durable state is involved.

Dependencies and integration points: This guards SCM background services that should run only when their SCM context allows them, especially services whose startup is delayed after safe mode.

Risks: The run test is timing-sensitive despite using a `TestClock`, because it verifies execution through a background thread with a timeout.

Test signals: `shouldRun` transitions, `getRunning` after stop, and at-least-once invocation of `scrubPipelines`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestBackgroundSCMService.java -->
