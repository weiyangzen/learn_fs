# sources/storage-engines/rocksdb/util/write_batch_util.h

## Purpose
`write_batch_util.h` declares a small write-batch inspection utility for RocksDB. Its core job is to walk a `WriteBatch` without applying mutations and collect the set of column-family IDs referenced by data-changing records in that batch. This supports code paths that need to know which column families a replicated, loaded, or externally supplied batch touches before choosing handles or replay behavior.

## Important APIs, Types, And Functions
`ColumnFamilyCollector` derives from `WriteBatch::Handler`. It owns an in-memory `std::unordered_set<uint32_t> column_family_ids_` and exposes it through `column_families() const`.

The private helper `AddColumnFamilyId(uint32_t)` inserts a column-family ID and always returns `Status::OK()`. All relevant mutation callbacks delegate to it: `PutCF`, `PutEntityCF`, `TimedPutCF`, `DeleteCF`, `SingleDeleteCF`, `DeleteRangeCF`, `MergeCF`, and `PutBlobIndexCF`.

Transactional or marker callbacks intentionally ignore payload and return OK: `MarkBeginPrepare`, `MarkEndPrepare`, `MarkRollback`, `MarkCommit`, `MarkCommitWithTimestamp`, and `MarkNoop`. That means the collector reports column families touched by write operations, not transaction marker metadata.

The free function `CollectColumnFamilyIdsFromWriteBatch(const WriteBatch& batch, std::vector<uint32_t>* column_family_ids)` is declared here and implemented in `util/write_batch_util.cc`. The implementation asserts the output pointer is not null, clears the output vector, iterates the batch with `ColumnFamilyCollector`, and copies the unordered-set contents to the vector only if iteration succeeds.

## Control Flow
Runtime flow is handler-driven. A caller passes a `WriteBatch` to `CollectColumnFamilyIdsFromWriteBatch()`, the function constructs `ColumnFamilyCollector`, and `WriteBatch::Iterate()` dispatches each encoded record to the matching virtual method. Data mutations flow through `AddColumnFamilyId()`, while prepare/commit/rollback/noop records are accepted without changing collector state. If `Iterate()` returns an error, the output vector remains cleared and no partial set is copied.

Inside `ColumnFamilyCollector`, there is no branching beyond callback selection by the `WriteBatch` iterator. Deduplication is delegated to `std::unordered_set`, so repeated operations on the same column family collapse to one ID.

## State And Persistence Behavior
State is entirely transient. `ColumnFamilyCollector` stores only the current walk's unique column-family IDs. It does not mutate the `WriteBatch`, does not persist metadata, and does not retain references to key/value `Slice` arguments. The returned vector has no deterministic ordering because it is populated from an `unordered_set`.

The utility returns `rocksdb::Status` through RocksDB's namespace macro. It propagates only the `WriteBatch::Iterate()` status; individual collector callbacks always return OK.

## Dependencies
The header depends on `<unordered_set>`, `<vector>`, `rocksdb/slice.h`, `rocksdb/status.h`, and `rocksdb/write_batch.h`. Its main external contract is `WriteBatch::Handler`; if RocksDB adds new write-record callback kinds that carry column-family IDs, this collector must be updated or those records will be silently omitted.

## Integration Points
Direct users found in this tree include `util/udt_util.cc`, `db/db_impl/db_impl_secondary.cc`, `db/db_impl/db_impl_follower.cc`, and `tools/ldb_cmd.cc`. `ldb_cmd.cc` also instantiates `ColumnFamilyCollector` directly. The utility implementation is listed in RocksDB build manifests such as `CMakeLists.txt`, `BUCK`, and `src.mk`.

## Risks And Edge Cases
The output order is intentionally unstable because of `unordered_set`; callers must treat the vector as a set unless they sort it themselves. The output pointer is guarded by `assert`, so null pointer misuse can become undefined behavior in release builds where assertions are disabled. The collector ignores transaction markers, which is correct for column-family mutation discovery but would be insufficient for code trying to analyze transaction lifecycles. The largest maintenance risk is drift from `WriteBatch::Handler`: any newly added CF-bearing operation needs a matching override.

## Test Signals
Good tests would build a `WriteBatch` with duplicate writes to the same column family, writes to multiple column families, range deletes, blob-index records, and transaction markers, then verify the resulting set and propagation of `Iterate()` errors. Existing integration signal comes from consumers in UDT, secondary/follower DB code, and `ldb` tooling, but this header itself has no direct test file in the searched output.
