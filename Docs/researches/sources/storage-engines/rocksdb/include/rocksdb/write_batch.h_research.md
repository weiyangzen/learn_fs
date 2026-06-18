<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/write_batch.h

Purpose: Defines `WriteBatch`, the standard serialized container for applying an ordered set of updates atomically to a RocksDB database and WAL. It also defines handler callbacks for replaying or inspecting serialized batch records.

Important APIs/types/functions: `SavePoint`, `WriteBatch`, and nested `WriteBatch::Handler` are central. Mutation APIs cover `Put`, timestamped `Put`, `SliceParts` variants, `TimedPut`, `PutEntity`, attribute-group `PutEntity`, `Delete`, `SingleDelete`, `DeleteRange`, `Merge`, and `PutLogData`. Management APIs include `Clear`, savepoint rollback/pop, `Iterate`, `Data`, `Release`, `GetDataSize`, `Count`, `Has*` content flags, `UpdateTimestamps`, checksum verification, WAL termination, constructors from serialized data, copy/move, and `SetMaxBytes`.

Control flow: Mutations append encoded records to `rep_` in insertion order and update count/content metadata. `Iterate` decodes `rep_` and dispatches each record to `Handler` callbacks, whose default implementations preserve old single-column-family behavior or return errors for unimplemented newer record kinds. Savepoints capture serialized size/count/flags and rollback truncates to a prior state.

State and persistence behavior: `rep_` is the durable serialized batch payload used for DB writes and WAL records. `PutLogData` persists only in WAL and does not consume a sequence number. Timestamp state tracks whether in-place timestamp update is needed and maps column-family ids to timestamp sizes when requested. Optional per-key protection bytes support checksum verification.

Dependencies and integration points: Implements `WriteBatchBase`; integrates with DB write path, WAL replay, transaction prepare/commit markers, `WriteBatchInternal`, Java JNI write batch bindings, and `WriteBatchWithIndex`.

Risks and edge cases: Multiple threads need external synchronization for mutations. Handler subclasses must implement non-default column-family callbacks or iteration returns errors. User-defined timestamp APIs require correctly appended timestamp bytes. `TimedPut` is experimental and can break snapshot immutability. `Release` transfers serialized data and clears the batch.

Test signals: `WriteBatchTest`, `WriteBatchHandlerTest`, threaded write batch tests, transaction tests, timestamp tests, checksum tests, and WAL recovery tests should validate encoding order, content flags, savepoints, handler dispatch, timestamp updates, WAL-only log data, protection checksums, and serialized constructor compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_batch.h -->
