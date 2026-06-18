# sources/storage-engines/foundationdb/fdbserver/workloads/DDBalance.cpp

Purpose: Defines `DDBalance`, a synthetic data-distribution stress workload that repeatedly moves many keys between logical bins to produce sustained key movement and latency metrics.

Important APIs/types/functions: `DDBalanceWorkload`, `ddbalanceSetup`, `ddbalanceSetupRange`, `ddBalanceMover`, `ddBalanceWorker`, `setKeyIfNotPresent`, `databaseWarmer`, `DDSketch<double>`, and counters for operations, retries, and bin shifts.

Control flow: Setup shuffles batched object ranges and writes initial keys into a random `currentbin`, optionally warming the database. `start` runs `moversPerClient` timed mover actors. Each mover picks a new destination bin, launches workers over slices of `nodesPerActor`, and each worker reads source keys, writes destination keys, clears sources, retries whole transaction chunks, and verifies it moved all expected keys.

State and persistence behavior: Persistent state is a set of formatted keys `(bin, object, mover, client)` with values derived from object number. Runtime state tracks current bin drift, measured latencies, and counters. Key-space drift can push future destination bins beyond the original `binCount` range to vary shard placement.

Dependencies/integration: It uses Native API transactions, `WorkloadUtils` database warming, deterministic random bin selection, Poisson pacing, and DDSketch percentile metrics.

Risks: `nodesPerActor = nodes / (actorsPerClient * clientCount)` can truncate coverage. The workload asserts on lost keys, so setup collisions or repeated failed reads become fatal. Edge-measurement discard changes metric denominators.

Test signals: `LostKeys` is the main correctness failure. Metrics include operations/sec, retries, bin shifts, and mean/median/p90/p98 latencies.
