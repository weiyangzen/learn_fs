# sources/storage-engines/foundationdb/fdbserver/core/LatencyBandConfig.cpp

## Purpose
Parses and compares latency-band configuration JSON for get-read-version, read, and commit request categories.

## Important APIs, Types, and Functions
- `operator==` and `operator!=` for `RequestConfig` compare dynamic type and fields.
- `RequestConfig::fromJson()` loads the `bands` array.
- `ReadConfig::fromJson()` also loads `max_read_bytes` and `max_key_selector_offset`.
- `CommitConfig::fromJson()` also loads `max_commit_bytes`.
- `LatencyBandConfig::parse()` validates JSON against `JSONSchemas::latencyBandConfigurationSchema` and returns an optional config.
- `LatencyBandConfig` equality compares GRV, read, and commit configs.

## Control Flow
Parsing returns empty optional for empty strings, invalid JSON, or schema mismatch. Valid JSON is wrapped as `JSONDoc`, then each request-category subdocument populates the corresponding config. Equality first checks dynamic type for request configs, then delegates to type-specific `isEqual()` implementations.

## State and Persistence Behavior
No durable state. Parsed configs hold in-memory sets of band thresholds and optional request limits.

## Dependencies and Integration Points
Depends on management API JSON helpers, schema validation, and the latency band schema. Consumers can store configuration as a `ValueRef` and call `parse()` before applying instrumentation or request classification.

## Risks and Edge Cases
`ReadConfig::isEqual()` and `CommitConfig::isEqual()` static-cast after the top-level operator checks type identity; direct calls with the wrong subtype would be unsafe. Invalid configuration is logged and ignored by returning empty optional. Band insertion into a set deduplicates thresholds and loses original order.

## Test Signals
No embedded tests. Useful coverage includes empty config, malformed JSON, schema mismatch, full valid configs, equality across same and different request config types, and limit-field parsing.
