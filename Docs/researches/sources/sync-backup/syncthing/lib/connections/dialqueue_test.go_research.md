# sources/sync-backup/syncthing/lib/connections/dialqueue_test.go

## sources/sync-backup/syncthing/lib/connections/dialqueue_test.go

Purpose: Tests `dialQueue.Sort` ordering and randomization behavior.

Important APIs/types/functions: `TestDialQueueSort` has subtests `ByLastSeen`, `OldConnections`, and `ShortLivedConnections`; helper `shortDevices` extracts short IDs for comparison.

Control flow and state: Recent devices are expected in strict newest-first order. Old entries are sorted into a stale suffix and shuffled repeatedly, with the test requiring both possible orders to appear enough times. Short-lived recent entries are treated like stale entries for ordering.

Dependencies and integration: Uses shared test device IDs, `time.Now`, and `protocol.ShortID`.

Risks and test signals: Randomized assertions can be flaky if randomness is biased, but repeated loops with broad thresholds make failures meaningful. Protects fairness semantics in the dial scheduler.
