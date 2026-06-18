# sources/storage-engines/foundationdb/fdbserver/workloads/DataDistributionMetrics.cpp

Purpose: Implements `DataDistributionMetrics`, a `KVWorkload` that stresses ordinary reads/writes while validating the raw data-distribution stats special range and key-selector semantics.

Important APIs/types/functions: `DataDistributionMetricsWorkload`, `ddRWClient`, `resultConsistencyCheckClient`, `_check`, `ddStatsRange`, `JSONSchemas::dataDistributionStatsSchema`, `schemaMatch`, `ReadYourWritesTransaction`, `RAW_ACCESS`, and timeout transaction options.

Control flow: `start` runs one stats-range consistency checker plus `actorCount` random read/write clients for `testDuration`, then waits five seconds. The checker repeatedly builds begin/end key selectors around random user-key intervals in `ddStatsRange`, reads with a large limit, and verifies the returned boundary keys match selector expectations. `check` on client 0 reads all DD stats, validates each JSON object against schema, counts shards, and computes average bytes.

State and persistence behavior: User data is randomly updated under `keyPrefix`-derived keys. System state is read through `ddStatsRange` with raw access. Runtime counters track commits and selector-result errors.

Dependencies/integration: Depends on `KVWorkload` node options, DD stats special keyspace, JSON schema definitions, Native API range behavior, and client timeout handling.

Risks: Timeouts are intentionally tolerated, but other special-range errors feed `onError`. The selector consistency assumptions can be broken by multi-RPC range reads, so the code guards only when `result.size() > 1`. Schema validation is strict and can fail on DD stats format changes.

Test signals: Any `errors` counter causes `TestFailure`. Other signals are `DataDistributionStatsSchemaValidationFailed`, `NumShards`, `AvgBytes`, and commit count.
