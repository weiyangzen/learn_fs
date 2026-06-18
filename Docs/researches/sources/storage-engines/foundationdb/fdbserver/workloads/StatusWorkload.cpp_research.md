# sources/storage-engines/foundationdb/fdbserver/workloads/StatusWorkload.cpp

## Purpose
`StatusWorkload` repeatedly fetches cluster status JSON, optionally validates it against a schema, optionally mutates latency-band configuration, and records status latency and response-size metrics.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `Status`. Important members are `testDuration`, `requestsPerSecond`, `maxAcceptableStatusLatency`, `enableLatencyBands`, `parsedSchema`, counters, and `worstLatency`. Key functions are `schemaCoverageRequirements`, `generateBands`, `configureLatencyBands`, and `fetcher`. The file also contains unit test `/fdbserver/status/schema/basic`.

## Control Flow
The constructor parses the requested status schema and registers schema coverage requirements. Setup may start `configureLatencyBands`, which writes randomized latency band configuration under `latencyBandConfigKey` using system-key and lock-aware options. Client 0 runs `fetcher` for `testDuration`, issuing Poisson-paced `StatusClient::statusFetcher` calls, serializing replies to measure size, tracking worst latency, and validating the JSON object against the parsed schema.

## State And Persistence Behavior
The workload can persist latency band configuration in system keyspace. It otherwise reads status data and maintains in-memory counters. The schema coverage hooks affect test coverage accounting rather than database state.

## Dependencies And Integration Points
It depends on `StatusClient`, JSON schema helpers, ManagementAPI system keys, `flow/UnitTest`, and status schemas from `fdbclient/Schemas.h`. The unit test exercises `schemaMatch` behavior for objects, arrays, enums, maps, type mismatches, and unexpected fields.

## Risks And Edge Cases
If schema validation fails, the workload logs `StatusWorkloadValidationFailed` but does not increment `errors`, so final `check` only fails on fetch errors or excessive latency. Latency-band configuration can continue independently and returns randomly after one or more writes.

## Test Signals
Metrics include requests, replies, average reply size, errors, and worst latency. Failure signals include `StatusWorkloadError`, `StatusWorkloadValidationFailed`, `StatusLatencyExceeded`, and schema coverage exceptions.
