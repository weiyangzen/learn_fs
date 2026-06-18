# sources/storage-engines/badger/stream_writer_test.go

## Purpose
This test file validates `StreamWriter` restore and incremental-ingest behavior across normal, managed, in-memory, encrypted, large-value, and stream-marker scenarios. It is the main behavioral evidence for direct SSTable ingestion.

## Important Tests and Helpers
- `getSortedKVList` builds a `z.Buffer` of protobuf KVs sorted by big-endian uint64 key.
- `TestStreamWriter1` verifies basic restore and reads in normal, managed, and in-memory modes.
- `TestStreamWriter2` and `TestStreamWriter3` check post-restore deletes and inserts through normal transactions.
- `TestStreamWriter4` validates oracle reinitialization after restore.
- `TestStreamWriter5` checks extreme byte-prefix keys survive reopen.
- `TestStreamWriter6` ensures multiple versions of the same logical key stay in the same table.
- `TestStreamWriterCancel`, `TestStreamDone`, `TestSendOnClosedStream`, and `TestSendOnClosedStream2` cover lifecycle and stream closure.
- `TestStreamWriterEncrypted`, `TestStreamWriterWithLargeValue`, and `TestStreamWriterIncremental` exercise encryption, large values, and incremental mode.

## Control Flow and State Behavior
Most tests create serialized KV buffers, call `NewStreamWriter`, `Prepare` or `PrepareIncremental`, `Write`, and `Flush`, then verify through Badger reads and iteration. Managed-mode tests set transaction read/commit timestamps explicitly after restore. Incremental tests repeatedly add small non-overlapping sets, verify existing data remains visible, and check that an intervening normal write leaves memtable data that causes `PrepareIncremental` to fail.

Closed-stream tests construct buffers with `StreamDone` markers and assert that sending another KV for the same stream either later or within the same buffer panics. The cancel test intentionally omits `Flush` and calls `Cancel` to ensure goroutines unblock and cleanup is idempotent enough for deferred use.

## Dependencies and Integration Points
The tests use Badger test helpers (`runBadgerTest`, `getTestOptions`), protobuf `pb.KV`, `z.Buffer`, direct transaction APIs, DB reopen, table metadata via `db.Tables`, and encryption options.

## Risks and Edge Cases
The tests assume sorted input unless deliberately testing same-key grouping. They validate many lifecycle hazards but do not prove safe concurrent calls from many goroutines despite `Write` being documented thread-safe. Some assertions rely on reopen success to catch manifest/table registration problems.

## Test Signals
The strongest signals are oracle timestamp repair, closed-stream panic enforcement, encrypted restore plus reopen, large-value managed mode, and incremental refusal when memtables contain data.
