# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/IdempotencyId.h

## Purpose
Defines compact representations and helpers for commit idempotency IDs. These IDs let commit proxies record and later detect previously accepted transaction batches so retry paths can return the original commit result instead of duplicating effects.

## Important APIs, Types, And Functions
`CommitResult` stores commit version and batch index. `IdempotencyIdsExpiredVersion` records the highest version that may have had IDs expired plus the expiration time. `IdempotencyIdRef` is a 16-byte compact value/reference type: invalid is `first == 0`; 16-byte IDs with an unambiguous first word can be stored inline; other valid IDs of length 16 through 255 use an external pointer. `dynamic_size_traits<IdempotencyIdRef>` serializes by copying the exposed string bytes. `IdempotencyIdKVBuilder` batches ID entries into key/value records by commit version and high-order batch-index byte. Free helpers check whether a KV contains an ID, build a single-key range, decode idempotency keys, expose JSON status, and clean leaked IDs.

## Control Flow
Commit-side code builds one or more idempotency KV records by setting the commit version, adding IDs with compatible high-order batch-index bytes, then calling `buildAndClear()`. Retry/lookup paths inspect persisted KVs with `kvContainsIdempotencyId()`. Cleanup scans and removes IDs older than a configured age, while preserving recent IDs needed for retry correctness.

## State And Persistence Behavior
The durable state is stored in FDB system keys described by the idempotency design: commit-version-keyed KVs containing IDs and batch indexes, plus the expired-version marker. `IdempotencyIdRef` often borrows memory, so lifetime is critical unless copied into an `Arena` or `Standalone`. Cleanup normally only handles failure leaks because successful commit paths are expected to expire IDs.

## Dependencies And Integration Points
The header depends on FDB key/value types, arenas, random utilities, serialization, JSON builder output, and a `PImpl` implementation for the builder. It integrates with commit proxies, transaction retry/idempotency logic, status reporting, and background cleanup actors.

## Risks And Test Signals
Risks include borrowed-memory lifetime bugs, ambiguous inline encoding for 16-byte IDs, batch-index grouping mistakes, incorrect expiration causing retries to lose idempotency guarantees, and cleanup racing with in-flight commits. Test signals should include encoding round trips, hash/equality coverage, builder grouping by high-order batch byte, lookup of positive/negative IDs, key decode/range construction, and failure-injection cleanup tests.
