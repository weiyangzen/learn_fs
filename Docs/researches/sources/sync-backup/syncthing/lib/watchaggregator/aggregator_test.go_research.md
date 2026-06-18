# Research: sources/sync-backup/syncthing/lib/watchaggregator/aggregator_test.go

## sources/sync-backup/syncthing/lib/watchaggregator/aggregator_test.go

Purpose: verifies the watch aggregator's coalescing, timing, batching, and in-progress suppression behavior.

Important APIs/functions: `TestMain` lowers `maxFiles` and `maxFilesPerDir`; `TestAggregate` validates path tree collapse; `TestInProgress` validates event suppression for Syncthing-owned writes; `TestDelay` and `TestNoDelay` validate timeout and remove batching; helpers include `testScenario`, `testAggregatorOutput`, `compareBatchToExpected`, and `getEventPaths`.

Control flow: tests create a mock aggregator with a basic folder config and feed events through either direct `newEvent` calls or the real `mainLoop`. Expected batches include path groups and timing windows. `testAggregatorOutput` consumes scan batches until all expectations are met or a ten-second timeout fires.

State and persistence: state is in-memory and time-driven. Tests mutate package-level caps and restore them after `m.Run`.

Dependencies and integration: uses `config.Wrapper`, `events.Logger`, `fs.Event`, and `protocol.LocalDeviceID`. Test signals are strong for logical batching but inherently time-sensitive; Darwin bypasses strict timing checks to avoid platform flakiness.
