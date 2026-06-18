# sources/storage-engines/foundationdb/fdbserver/workloads/BulkSetup.h

## Purpose
`BulkSetup.h` provides reusable templated setup helpers for workloads that need to populate large key ranges. It partitions a logical node/key index space across clients, creates range insertion jobs, writes generated key-value pairs with controlled conflict behavior and optional rate limiting, tracks insertion milestones, and optionally waits for data distribution to settle or warms the database.

## Important APIs, Types, And Functions
The header defines the `hasAuthToken` SFINAE helper and `setAuthToken`, allowing workloads with a `setAuthToken(Transaction&)` method to opt into authenticated transactions. Core actors are `checkRangeSimpleValueSize`, `setupRange`, `setupRangeWorker`, `trackInsertionCount` (declared here), `waitForLowInFlight`, and `bulkSetup`. The template parameter `T` is expected to expose `operator()(uint64_t)`, `keyForIndex`, `clientId`, `clientCount`, `description`, and optionally `dbInfo`.

## Control Flow
`bulkSetup` computes each client's node slice, optionally short-circuits if first/last keys are already present, smears start time, estimates a range size targeting about 10 KB per insertion transaction, builds shuffled range jobs, and launches 40 `setupRangeWorker` actors. Each worker pops jobs, calls `setupRange`, periodically persists `keycount|client|actor` and `bytesstored|client|actor`, and rate-limits by delaying until the computed next start. After all workers and optional insertion tracking complete, `bulkSetup` sends setup timing/rates, optionally waits for low data-in-flight, and optionally runs `databaseWarmer`.

## State And Persistence
Persistent state is the generated data plus optional progress keys `keycount|...` and `bytesstored|...`. `setupRange` writes all keys blind with `AddConflictRange::False` after adding one write conflict range over the whole generated span. If `valuesInconsequential` is true, it may treat existing first/last keys as enough evidence that the range is already loaded.

## Dependencies And Integration Points
The helpers use native transactions, tester workload utilities, `QuietDatabase`/`databaseWarmer`, `getDataInFlight`, simulation speed-up flags, auth token hooks, and deterministic randomness. They are shared by workload files that generate repeatable key/value records via a workload object.

## Risks
`jobs` is a shared vector popped by many actors in the same Flow thread model; it relies on cooperative actor scheduling rather than external locking. In speed-up simulation mode, existence reads are skipped to avoid `transaction_too_old`, which means blind writes may repeat existing data. The simple first/last presence check can produce false positives when interior data is missing. `waitForLowInFlight` can time out or surface attribute lookup errors depending on DD initialization.

## Test Signals
Trace events include `BulkSetupStart`, `<description>SetupStart`, `BulkSetupRangeAlreadyPresent`, `BulkRangeNotFound`, `CheckRangeError`, `BulkSetupFailed`, `SetupLoadComplete`, `DynamicWarming`, `DynamicWarmingDone`, and `<description>SetupOK`. Consumers typically use the `setupTime` and `ratesAtKeyCounts` promises as workload metrics.
