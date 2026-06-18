# sources/storage-engines/foundationdb/fdbserver/workloads/FastTriggeredWatches.cpp

Purpose: Exercises watch trigger latency by setting watches on random keys, changing those keys, and asserting the watch-trigger-to-visible-read version lag remains bounded.

Important APIs/types/functions: `FastTriggeredWatchesWorkload`, `_setup`, `_start`, `setter`, `keyForIndex`, `ReadYourWritesTransaction`, `watch`, `getCommittedVersion`, `SERVER_KNOBS->VERSIONS_PER_SECOND`, and `MAX_VERSIONS_IN_FLIGHT`.

Control flow: Client 0 initializes every other key to a default value. During start, it repeatedly chooses a key and optional random value/clear, starts a delayed setter transaction, then loops reading the key. If the desired value is not visible, it creates a watch, commits it with a dummy conflict range, waits for the watch, then reads again. After the setter completes, it computes version delta and asserts it is below the allowed threshold unless versions in flight are already high.

State and persistence behavior: Persistent state is a fixed key set generated from encoded doubles in fixed-width byte strings. Values are set or cleared. Runtime state includes last read version, watch commit version, and counters, though operation/retry counters are not incremented in the current code.

Dependencies/integration: Disables `Attrition`, uses watches, RYW transactions, server knobs, deterministic key generation, and tester metrics.

Risks: Recoveries can bump versions enough to violate the assertion, hence attrition is disabled. The `clients` vector is unused for the main actor, so `check` mostly returns true unless future code adds clients. Version-delta assertion is timing-sensitive.

Test signals: Assertion failure in `_start`, `FastWatchError`, and latency/counter metrics, though counters may remain zero.
