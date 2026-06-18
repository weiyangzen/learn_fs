# sources/storage-engines/foundationdb/fdbserver/tester/CustomShardConfigWorkload.cpp

Purpose: Randomly exercises data-distribution user range configuration map behavior during simulation tests, including default ranges, overlapping updates, snapshots, and per-key lookup verification.

Important APIs/types/functions: `customShardConfigWorkload(Database const& cxUnsafe)` constructs a `ReadYourWritesTransaction`, uses `DDConfiguration().userRangeConfig()`, calls `updateRange`, `getSnapshot`, and `getRangeForKey`, and verifies expected `DDRangeConfig` values.

Control flow: The actor loops until commit succeeds. Each attempt sets system-key and lock-aware options, optionally initializes the all-keys default range, optionally applies fixed test ranges, verifies a table of query keys against both database-backed map lookups and the full snapshot, commits, and retries through `tr.onError` on failure.

State and persistence behavior: Mutates system-key backed data-distribution range configuration when enabled by random choices. The `RangeConfigMap` is optional because state variables need default construction around non-default-constructible versioned map internals.

Dependencies and integration points: Depends on `DataDistributionConfig`, `FDBTypes`, deterministic random, transaction options, and `customShardConfigWorkload` declaration in `tester.h`. `runTests7` invokes it with 25% probability in simulated database tests.

Risks: It writes system configuration during tests, so failures can affect subsequent test setup if not isolated by simulation cleanup. It uses `ASSERT` for verification, causing hard failures. Random branches mean any single run may skip parts of the behavior.

Test signals: `CODE_PROBE` and trace events (`KeyRangeConfigSetDefault`, `KeyRangeConfigSetTestRanges`, `KeyRangeConfigCommitted`, `KeyRangeConfigCommitError`) show which branches ran. Assertions validate lookup and snapshot consistency.
