<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/stats.go -->
# sources/sync-backup/kopia/tests/robustness/engine/stats.go

This file tracks aggregate robustness engine counters and per-action runtime/error statistics. `Stats` stores start/end timestamps, total action counts, completed/error counts, and a map from `ActionKey` to `ActionStats`; `ActionStats` records count, total runtime, and error count. `Engine.Stats` combines current-run and cumulative statistics into a string for logs.

Important methods include `Stats.Stats`, `ActionStats.AverageRuntime`, `ActionStats.Record`, `statsUpdateCounters`, `statsIncrActionCountAndLog`, and `statsUpdatePerAction`. Control flow increments global counters when actions start and complete, logs progress every `statsLogFrequency`, records runtime from start timestamps, and updates cumulative state that `metadata.go` persists.

The state model separates current run stats from cumulative stats, using `clock.Now` for testable time. Dependencies are the engine action model and metadata persistence. Risks include divide-by-zero protection depending on count checks, log noise in long randomized tests, and inconsistent stats if an action entry is started but never completed due to process death. Signals are indirect through robustness logs and persisted stats restoration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/stats.go -->
