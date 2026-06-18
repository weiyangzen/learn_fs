<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TagThrottle.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TagThrottle.h

## Purpose
`TagThrottle.h` defines transaction tag storage, system-key encoding for manual and automatic tag throttles, client-visible throttle records, commit-cost estimation state, and templated APIs for listing, adding, removing, expiring, and enabling tag throttles.

## Important APIs, Types, and Functions
Important types include `TransactionTagRef`, `TransactionTag`, `TagSet`, dynamic serialization traits for `TagSet`, `TagThrottleType`, `TagThrottledReason`, `TagThrottleKey`, `TagThrottleValue`, `TagThrottleInfo`, `ClientTagThrottleLimits`, `ClientTrCommitCostEstimation`, and maps keyed by transaction tag. `ThrottleApi` exports `getValidAutoEnabled`, `getRecommendedTags`, `getThrottledTags`, `signalThrottleChange`, `updateThrottleCount`, `unthrottleMatchingThrottles`, `expire`, `unthrottleAll`, `unthrottleTags`, `throttleTags`, and `enableAuto`.

## Control Flow
`TagSet` serializes as length-prefixed tag bytes and deserializes into request arena-backed refs. Listing APIs create transactions, read system keys, retry on errors, and convert each key/value to `TagThrottleInfo`. Throttle changes set system-key access, optionally update the manual throttle count against the configured limit, write or clear throttle keys, signal changes with a versionstamped atomic op, and commit with retry loops.

## State and Persistence Behavior
Throttle records live under `tagThrottleKeys`, with manual and automatic prefixes separated by `tagThrottleAutoKeysPrefix`. `tagThrottleAutoEnabledKey` controls auto behavior, `tagThrottleLimitKey` and `tagThrottleCountKey` enforce manual throttle count, and `tagThrottleSignalKey` wakes watchers. `TagThrottleValue` serialization is protocol-versioned and includes rate, expiration, initial duration, and reason.

## Dependencies and Integration Points
The header depends on Flow arenas, errors, network time, thread-future bridging, FDB options, FDB types, and commit transaction types. It integrates with fdbcli tag throttle commands, ratekeeper, commit proxies, storage-server busy tag reporting, and client transaction commit-cost accounting.

## Risks and Edge Cases
`TagSet` refs can share the containing request arena, so persisting deserialized tag refs beyond arena lifetime is unsafe. Manual throttle count updates must stay atomic with throttle key changes to avoid count drift. `getRecommendedTags` returns an empty vector when auto throttling is enabled, which callers must interpret correctly. Expiration uses local `now()`, so clock differences are handled differently from serialized client throttle limits, which convert expiration to a duration.

## Test Signals
Relevant tests include tag throttle CLI/API tests, manual count limit tests, auto enable/disable and recommendation tests, expiration tests, commit proxy throttling behavior, serialization compatibility for `TagThrottleValue`, and arena lifetime stress around serialized `TagSet` requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TagThrottle.h -->
