# sources/storage-engines/badger/stream_writer.go

## Purpose
This file implements `StreamWriter`, Badger's fast ingest path for data produced by streams. It writes sorted, non-overlapping stream ranges directly into SSTables and value logs, bypassing normal transactional write amplification and compactions. It supports destructive restore (`Prepare`) and incremental ingest (`PrepareIncremental`).

## Important APIs, Types, and Functions
- `DB.NewStreamWriter` constructs a writer with shared throttle and per-stream sorted writers.
- `Prepare` drops all existing data and installs a `done` callback to restore DB services.
- `PrepareIncremental` stops writes/compactions, checks memtables are empty, finds a target level above existing data, and may call `Flatten`.
- `Write` decodes protobuf KVs from a `z.Buffer`, groups by `StreamId`, writes values to the value log, feeds per-stream `sortedWriter`s, and handles `StreamDone` markers.
- `Flush` closes all writers, updates the oracle for unmanaged DBs, waits on asynchronous table creation, sorts level tables, syncs directories, and validates levels.
- `Cancel` unblocks writer goroutines and restores services without calling `dropAll`.
- `sortedWriter.Add`, `send`, `Done`, and `createTable` enforce sorted keys and build/register SSTables.

## Control Flow and State Behavior
`Write` first scans the incoming buffer. It tracks closed stream IDs within the buffer and panics if a KV appears after a done marker. It updates `maxVersion`, initializes `prevLevel` to the number of levels on first full write, converts protobuf fields into `Entry` values with timestamped keys, and groups them into value-log write requests. Under `writeLock`, the value log is written before requests are sent to sorted writer goroutines. Each sorted writer consumes requests serially, converts entries to `ValueStruct`s or value pointers, and appends to a table builder. Capacity boundaries flush builders asynchronously through a throttle.

`Flush` is the durability barrier. For unmanaged mode, it stops and recreates the oracle so future transaction timestamps advance beyond streamed versions and marks watermarks complete. Table creation reserves file IDs, writes in-memory or disk SSTables, records manifest create changes, inserts tables into the target level, and releases the table open reference.

## Dependencies and Integration Points
This code integrates with `DB.dropAll`, `prepareToDrop`, compaction control, value log write requests, manifest changes, level controller, table builder/opening, and oracle timestamp management. It consumes buffers produced by `Stream.KVToBuffer` and protobuf `pb.KV`.

## Risks and Edge Cases
The API is dangerous on active DBs: `Prepare` deletes existing data and assumes exclusive bootstrap use. Input must be sorted per stream and streams must not overlap; `sortedWriter.Add` rejects non-increasing timestamped keys. `StreamDone` closes a stream permanently. Partial writes after `Cancel` remain until a later `Prepare` drops them. Incremental mode refuses non-empty memtables and relies on level placement to avoid compaction conflicts.

## Test Signals
`stream_writer_test.go` covers normal, managed, and in-memory restore; post-restore writes/deletes; oracle reinitialization; boundary keys; same-user-key table grouping; cancel behavior; done markers and closed-stream panics; encrypted writes; large values; and repeated incremental ingestion.
