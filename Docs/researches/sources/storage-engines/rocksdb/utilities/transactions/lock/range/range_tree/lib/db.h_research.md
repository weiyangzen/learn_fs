# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/db.h

## Purpose
`db.h` is a compact BerkeleyDB/PerconaFT compatibility shim used by the vendored range-tree lock code. It defines the DBT key container, legacy engine-status row shape, and numeric error/flag constants expected by the locktree sources.

## Important APIs, Types, And Functions
`DBT` is forward-declared and then defined as `__toku_dbt { void *data; size_t size; size_t ulen; uint32_t flags; }`. `simple_dbt` is present but marked unused. `TOKU_ENGINE_STATUS_ROW_S` models status rows with `keyname`, `columnname`, `legend`, display/include enums, and a union of value forms.

Constants include `DB_LOCK_DEADLOCK`, `DB_LOCK_NOTGRANTED`, `DB_NOTFOUND`, `DB_KEYEXIST`, DBT allocation flags, and `TOKUDB_OUT_OF_LOCKS`. `lock_wait_callback` is a two-transaction callback typedef.

## Control Flow
There is no runtime control flow. This header supplies ABI-like names and status/error values consumed by locktree, OMT, DBT helpers, and status plumbing.

## State And Persistence Behavior
No state is owned here. The DBT struct is a borrowed or caller-owned buffer descriptor unless helper code clones or frees it. Status row values are filled elsewhere by `LTM_STATUS_S` and the manager.

## Dependencies
Only `<stdint.h>` and `<sys/types.h>` are included. Many downstream files assume this header's constants match the old PerconaFT convention and map them to RocksDB statuses at higher layers.

## Integration Points
`comparator.h`, `locktree.h`, `range_buffer`, wait-graph code, and OMT-backed containers use these types and constants. It is a narrow compatibility boundary between RocksDB transaction code and imported PerconaFT range-lock internals.

## Risks And Edge Cases
Changing numeric error codes can break callers that translate legacy return codes. `DBT::data` is mutable even in logically const use, so ownership and constness must be enforced by convention. `ulen` and `flags` are only partially meaningful in this port.

## Test Signals
Compilation of the range-tree subtree is the primary signal. Runtime coverage comes indirectly from range-lock tests that exercise `DB_LOCK_NOTGRANTED`, `DB_LOCK_DEADLOCK`, and DBT endpoint comparisons.
