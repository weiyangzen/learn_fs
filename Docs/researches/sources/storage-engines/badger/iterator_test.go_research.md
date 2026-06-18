# sources/storage-engines/badger/iterator_test.go

## Purpose
`iterator_test.go` provides focused coverage for iterator table selection, timestamp filtering, prefix/key iteration, read-only empty iteration, and a benchmark for prefix-optimized single-key lookups.

## Important APIs, Types, and Functions
- `tableMock`: minimal `table.TableInterface` for `pickTable`.
- `TestPickTables`: validates prefix overlap logic and a regression involving binary prefixes.
- `TestPickSortTables`: builds real SST tables and validates `IteratorOptions.pickTables` range filtering.
- `TestIterateSinceTs`: writes many keys and asserts iterator versions are at or above `SinceTs`.
- `TestIterateSinceTsWithPendingWrites`: verifies pending transaction writes with version 0 are still visible.
- `TestIteratePrefix`: manual, multi-cache-mode prefix/key iterator coverage.
- `TestIteratorReadOnlyWithNoData`: ensures read-only empty DB iterator construction does not crash.
- `BenchmarkIteratePrefixSingleKey`: measures lookup performance with `Prefix` set for a single key.

## Control Flow and State
The tests mix pure table-range logic, real table construction with `buildTable`, and DB-level write/read flows. Prefix iteration tests use `NewIterator` and `NewKeyIterator`; benchmark setup writes enough keys to produce many SSTables, then repeatedly seeks random keys with prefix filtering.

## Persistence Behavior
Real DB tests persist temporary SST/value-log data and reopen in read-only mode for one scenario. The table-picking tests rely on generated SST table metadata, including smallest/biggest keys and max versions.

## Dependencies and Integration Points
Depends on `IteratorOptions`, table builders, Badger test helpers, `options.OnTableAndBlockRead`, `y.KeyWithTs`, `DB.Ranges`, and filesystem walking for SST counts.

## Risks and Edge Cases
`TestIteratePrefix` is manual, leaving broad prefix counting mostly outside normal CI. Benchmarks are performance signals, not correctness gates. `TestPickSortTables` uses table refs and defers `DecrRef`, so future table refcount changes could affect test setup.

## Test Signals
Strong signal for prefix table pruning and timestamp filtering. Complements `db_test.go` iterator coverage by exercising internal picker functions directly.
