# sources/storage-engines/foundationdb/fdbclient/IdempotencyId.cpp

## Purpose
`IdempotencyId.cpp` implements storage, lookup, status, and cleanup for commit idempotency IDs. It batches multiple ids into system keys grouped by commit version and high-order batch-index byte, supports lookup of a specific id in a stored value, reports metadata status, and clears old idempotency entries safely by age.

## Important APIs, Types, And Functions
`IdempotencyIdKVBuilderImpl` and `IdempotencyIdKVBuilder` accumulate commit version, batch-index high byte, timestamp, id length, id bytes, and low-order batch byte. Lookup and encoding helpers are `kvContainsIdempotencyId()`, `makeIdempotencySingleKeyRange()`, `decodeIdempotencyKey()`, and private actor `getBoundary()`. Public actors `getIdmpKeyStatus()` and `cleanIdempotencyIds()` expose observability and garbage collection.

## Control Flow
Callers set the commit version, add valid ids with monotonically compatible batch indexes, and call `buildAndClear()` to produce a single `KeyValue`. `kvContainsIdempotencyId()` first uses `memmem` where available to skip most non-matches, then parses the binary value exactly and returns `CommitResult` containing decoded commit version and full batch index. `getIdmpKeyStatus()` retries a transaction that reads estimated size, expired-version metadata, and oldest key boundary. `cleanIdempotencyIds()` finds the oldest and youngest idempotency entries, checks age against `minAgeSeconds`, narrows a candidate delete range by version until the youngest key in the range is old enough, clears the final prefix range, records expired version/time, and commits with conflict range protection.

## State And Persistence Behavior
Idempotency metadata is persisted in `idempotencyIdKeys`, with keys encoding big-endian commit version and high-order batch index. Values begin with wall-clock timestamp and then repeated `(length, id bytes, low-order batch index)` tuples. Cleanup persists progress in `idempotencyIdsExpiredVersion`. Builder state is reset after `buildAndClear()` but retains commit version until changed.

## Dependencies And Integration Points
The file uses `fdbclient/IdempotencyId.h`, `KeyBackedTypes`, `ReadYourWrites`, `SystemData`, tuple/binary serialization, `JsonBuilderObject`, transaction options for system keys and lock-aware reads, and Flow unit tests. It integrates with commit idempotency mutation building and management/status code that surfaces idempotency key size and age.

## Risks And Edge Cases
`IdempotencyIdKVBuilder::add()` asserts that all ids in one value share the same high-order batch byte, so callers must segment batches correctly. IDs are length-prefixed with one byte, matching generated test lengths up to 255. `kvContainsIdempotencyId()` protects against substring false positives by parsing, but corrupt values can throw/assert through `BinaryReader`. Cleanup uses wall-clock age recorded at write time; clock anomalies can delay or hasten deletion. The binary-search-like cleaner trades precision for bounded range clearing and must avoid deleting young ids.

## Test Signals
Local tests cover builder format, id lookup, commit version and batch index reconstruction, hash/equality behavior, missing-id lookup, and serialization round-trips for `IdempotencyIdRef`. Additional useful tests would exercise cleaner range selection, expired-version metadata, and Windows fallback without `memmem`.
