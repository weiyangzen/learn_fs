## sources/object-store/garage/src/api/k2v/range.rs

Purpose: shared K2V table range pagination utility for index, read-batch, and delete-batch endpoints.

Important APIs/types/functions: `read_range<F>`.

Control flow: calculates initial `start` and whether to ignore that start depending on prefix/start/reverse. It rejects starts outside prefix. Reverse prefix scans start at `key_after_prefix(prefix)` and ignore the synthetic boundary. It repeatedly calls `table.get_range` with bounded batch size, applies prefix/end/limit checks, sets `more` and `nextStart` when limit is exceeded, and advances by last returned sort key while avoiding duplicates.

State/persistence: read-only table access through `garage_table`.

Dependencies/integration: generic over `TableSchema<S=String>` with sharded replication. Used by K2V index and batch handlers.

Risks: pagination correctness depends on table sort order and `EnumerationOrder`. Reverse prefix scans can fail for prefixes without a successor. The computed `n_get` uses limit minus entries plus two; very small/large limits should be carefully tested.

Test signals: no local tests; endpoint pagination tests should cover prefix/start/end/reverse interactions.
