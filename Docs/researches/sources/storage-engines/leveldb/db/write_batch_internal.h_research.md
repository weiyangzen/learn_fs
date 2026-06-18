# sources/storage-engines/leveldb/db/write_batch_internal.h

Purpose: exposes internal-only helpers for manipulating `WriteBatch` representation fields that are intentionally hidden from the public API.

Important APIs and types: `WriteBatchInternal::Count`, `SetCount`, `Sequence`, `SetSequence`, `Contents`, `ByteSize`, `SetContents`, `InsertInto`, and `Append`.

Control flow: DB internals set sequence/count metadata, obtain raw contents for log writing, restore raw contents from log records, and insert batch contents into a `MemTable`.

State and persistence behavior: this header is the gateway to the persistent batch wire format. `Contents` returns a `Slice` over `rep_`, so the batch must outlive the slice.

Dependencies and integration: friends with public `WriteBatch`, uses `SequenceNumber` and `MemTable`. Recovery, repair, tests, and DB write paths include it.

Risks and edge cases: bypasses encapsulation and can create invalid batches if callers set inconsistent contents/counts. It is not a public compatibility promise beyond LevelDB internals.

Test signals: exercised directly by write-batch and recovery tests.
