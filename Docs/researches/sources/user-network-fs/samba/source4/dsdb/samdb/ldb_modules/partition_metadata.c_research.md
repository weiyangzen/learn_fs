# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition_metadata.c

## Purpose

`partition_metadata.c` manages `sam.ldb.d/metadata.tdb` for the DSDB partition module. The TDB stores global sequence metadata, including `SEQ_NUM` and the schema sequence key, and provides the lock semantics used by `partition.c` to coordinate reads and commits across multiple independently locked partition databases.

The file intentionally uses TDB for metadata even when partition backends can be different database types, because the partition module relies on TDB read/write lock blocking semantics for cross-partition consistency.

## Important APIs and Functions

`partition_metadata_get_uint64()` fetches a TDB key, parses it as an unsigned 64-bit decimal value, and returns a caller-provided default if the key does not exist.

`partition_metadata_set_uint64()` stores a decimal unsigned 64-bit value using `TDB_INSERT` or `TDB_MODIFY`.

`partition_metadata_inc_schema_sequence()` increments `DSDB_METADATA_SCHEMA_SEQ_NUM` inside an active metadata transaction, falling back from modify to insert when the key is missing.

`partition_metadata_open()` opens `sam.ldb.d/metadata.tdb`, optionally creating `sam.ldb.d`, applying loadparm TDB flags plus `TDB_SEQNUM`, respecting `LDB_FLG_NOSYNC`, and mapping permission errors to `LDB_ERR_INSUFFICIENT_ACCESS_RIGHTS`.

`partition_metadata_init()` allocates `partition_metadata`, opens the DB if present, or creates it as a migration path when missing.

`partition_metadata_sequence_number()` returns `SEQ_NUM` under a full partition read lock so the sequence observed is not ahead of the visible partition state.

`partition_metadata_sequence_number_increment()` requires an active metadata transaction, initializes `SEQ_NUM` from the older sum-of-partitions sequence if the stored value is zero, increments it, and stores the result.

`partition_metadata_read_lock()` and `partition_metadata_read_unlock()` implement recursive read-lock accounting around `tdb_lockall_read()`/`tdb_unlockall_read()`, avoiding lock operations while a TDB transaction is active.

`partition_metadata_start_trans()`, `partition_metadata_prepare_commit()`, `partition_metadata_end_trans()`, and `partition_metadata_del_trans()` wrap TDB transaction start, prepare, commit, and cancel while maintaining `in_transaction`.

## Control Flow

Initialization is lazy. Callers ensure `partition_private_data` exists, then `partition_metadata_init()` creates the metadata wrapper and attempts an existing open. If the file is missing, it creates the directory/file and leaves sequence keys to be filled by later transaction-time increments.

Sequence reads call back up to `partition_read_lock()`, which locks all databases in the ordering defined by `partition.c`, then reads `SEQ_NUM` defaulting to zero, and unlocks. Sequence increments are only allowed inside a metadata transaction. If `SEQ_NUM` is zero, the code obtains the legacy sum of primary and partition sequence numbers and inserts that as the starting value before incrementing.

Schema sequence increments mirror regular sequence handling but use `DSDB_METADATA_SCHEMA_SEQ_NUM` and are triggered by the schema-update extended operation in `partition.c`.

Transaction functions are thin wrappers around TDB APIs, but their counters are part of the module's correctness contract. Prepare does not decrement the transaction count; commit/cancel do.

## State and Persistence Behavior

Persistent state lives in `sam.ldb.d/metadata.tdb`. Values are stored as decimal strings rather than binary integers. The primary key in this file is `SEQ_NUM`; schema sequence uses the DSDB metadata schema sequence key from Samba headers.

Process-local state includes the `tdb_wrap` pointer, `in_transaction`, and `read_lock_count`. `read_lock_count` allows nested read locks to avoid repeated TDB lock calls and ensures only the outermost unlock releases the TDB read lock when no transaction is active.

## Dependencies and Integration Points

The file depends on TDB/TDB wrap, loadparm TDB flags, `ldb_relative_path()`, filesystem `stat()`/`mkdir()`, Samba string-to-integer conversion, and functions implemented in `partition.c` such as `partition_read_lock()` and `partition_sequence_number_from_partitions()`.

It is called by partition transaction/read-lock paths and by partition extended operations for sequence number and schema update handling.

## Risks and Edge Cases

All mutation APIs require `data->metadata->in_transaction > 0`. Calling sequence increments outside the partition transaction flow fails with operations errors.

`partition_metadata_set_uint64()` chooses strict insert or modify. Missing-key modify failures are handled explicitly for schema sequence but not for regular post-initialization increments after the zero migration path. Any unexpected key loss after initialization could surface as an operations error.

Read-lock accounting assumes balanced lock/unlock calls. `partition_metadata_read_unlock()` decrements even when the count is not one; underflow or unlock-without-lock would corrupt the counter and can cause mismatched TDB locking.

`partition_metadata_sequence_number()` recursively enters the higher-level partition read-lock path from metadata code. This is intentional for visibility consistency, but changes to lock ordering can create deadlocks.

The error string in the parse failure path contains a typo (`converision`), which is harmless but visible in diagnostics.

Creation mode uses `O_CREAT` but opens read/write and mode `0660`; deployments with unexpected permissions can fail initialization before partitions are available.

## Test Signals

Tests should cover opening existing metadata, creating missing metadata during migration, permission-denied mapping, reading absent `SEQ_NUM` as zero, incrementing sequence within and outside transactions, initializing zero sequence from legacy partition sums, schema sequence insert-then-modify behavior, transaction prepare/commit/cancel counter balance, nested metadata read locks, sequence reads under concurrent writer transactions, `LDB_FLG_NOSYNC` flag propagation, and recovery from TDB store/fetch errors.
