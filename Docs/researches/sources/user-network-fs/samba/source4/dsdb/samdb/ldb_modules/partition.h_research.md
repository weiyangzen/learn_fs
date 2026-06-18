# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.h

## Purpose

`partition.h` is the shared internal header for the Samba DSDB partition module implementation. It pulls in the required LDB, TDB, DSDB, utility, locale, and loadparm headers, defines the core private data structures used across `partition.c`, `partition_init.c`, and `partition_metadata.c`, and includes the generated `partition_proto.h` prototypes.

This header is not a public API in the general Samba sense; it is the private contract among the partition module compilation units.

## Important Types

`struct dsdb_partition` represents one backend naming context. It contains the top module used to send requests into that backend chain, the `dsdb_control_current_partition` payload identifying the partition DN, the backend URL, the original `@PARTITION` record blob used to detect newly added partitions, and a `partial_replica` flag used for global-catalog/no-GC search routing.

`struct partition_module` maps an optional partition DN to a module list. A `NULL` DN represents the default module list. `partition_init.c` uses these records to decide which module chain to load for each backend.

`struct partition_metadata` wraps the metadata TDB handle plus in-memory counters for active metadata transactions and recursive read locks.

`struct partition_private_data` is the module-private state shared by all partition implementation files. It contains the sorted partition array, the special-DN replicate list, metadata state, per-partition module mappings, cached primary metadata sequence, global transaction nesting count, an optional forced module configuration message supplied by the higher Samba4 module, and the backend DB store type such as `tdb`.

## Integration Points

The header includes `tdb_wrap.h` because metadata storage is explicitly TDB-backed, even when partition databases may be other backends. It includes `dsdb/samdb/samdb.h` and `dsdb/samdb/ldb_modules/util.h` for DSDB controls, extended operations, and module helper APIs used throughout the implementation.

`partition_proto.h` is generated and supplies cross-file prototypes, so function additions in any implementation file must be reflected by the build's prototype generation process.

## State and Persistence Behavior

The structures in this header define both runtime and persistence-facing state. `backend_url`, `orig_record`, `partial_replica`, and `backend_db_store` are derived from persistent `@PARTITION` metadata. `partition_metadata` points at the persistent `sam.ldb.d/metadata.tdb`. `metadata_seq`, `in_transaction`, and `read_lock_count` are process-local coordination values layered on top of persistent state.

Memory ownership is talloc-based. Most child objects are allocated under `partition_private_data`, individual `dsdb_partition` objects, or their control structures. Correct talloc parentage matters because partitions and their module chains are long-lived module-private state.

## Risks and Edge Cases

Because this header defines shared structs directly, changes are high blast-radius. Adding fields can require updates to initialization, reload, transaction, and teardown paths across all three implementation files.

The sorted partition array and `orig_record` comparison are implicit contracts: routing code assumes ordering, while reload code uses original record blobs to skip already loaded partitions. If DN normalization or record encoding changes, both contracts need review.

`partial_replica` drives visibility under `DSDB_CONTROL_NO_GLOBAL_CATALOG`; incorrect initialization can leak or hide global catalog data.

`partition_metadata` counters must stay consistent with actual TDB transaction/read-lock state. Since the counters are defined here and manipulated across files, mismatched increment/decrement logic can lead to deadlocks or transaction errors.

## Test Signals

Structural test signals are indirect: partition initialization should build correctly sorted `dsdb_partition` arrays, module selection should honor explicit and default `partition_module` records, metadata initialization should populate `partition_metadata`, transaction/read-lock nesting should leave counters balanced, and partial-replica flags should affect search routing. Build tests should ensure `partition_proto.h` remains synchronized after changing cross-file functions.
