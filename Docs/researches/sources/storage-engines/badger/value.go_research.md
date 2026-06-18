# sources/storage-engines/badger/value.go

## Purpose
This file implements Badger's value-log core: entry encoding/decoding safety, append/rotation of `.vlog` files, reading by value pointer, value-log garbage collection and rewrite, discard-stat updates, iterator-safe deletion, and dynamic value-threshold tracking.

## Important APIs, Types, And Functions
Important constants are value metadata bits (`bitDelete`, `bitValuePointer`, `bitTxn`, `bitFinTxn`) and `vlogHeaderSize`. `safeRead.Entry` decodes a header, decrypts key/value bytes when enabled, and validates CRC. `valueLog` owns `filesMap`, `maxFid`, `writableLogOffset`, `garbageCh`, and `discardStats`. Main methods include `init`, `open`, `Close`, `createVlogFile`, `write`, `Read`, `readValueBytes`, `rewrite`, `pickLog`, `runGC`, `updateDiscardStats`, and `validateWrites`. `request` and `requests` carry batched write entries and value pointers with ref-counted lifecycle. `vlogThreshold` tracks histogram-based dynamic threshold updates.

## Control Flow
Open populates existing `.vlog` files, opens them read/write or read-only, deletes empty non-latest logs, scans/truncates the latest log to the last valid offset, then creates a fresh writable log. Writes validate total request sizes against the 32-bit pointer offset limit, append large values directly into the mmap-backed current log, strip transaction marker bits from value-log copies, update metrics and threshold histograms, and rotate logs when size or entry count limits are crossed. Reads lock the target log file, read the byte range, optionally verify checksum, decrypt, decode the header, and return the value slice plus an unlock callback.

## State And Persistence Behavior
Persistent state is the `.vlog` file set under `ValueDir`, discard stats, mmap file sizes, and value pointers stored in LSM entries. `SyncWrites` causes append syncs; otherwise `sync` explicitly syncs the latest log when needed. GC rewrite scans an old log, skips deleted/expired/stale entries, re-inserts still-current values via `batchSet`, and deletes or defers deletion of the old file depending on active iterator count. `dropAll` deletes value logs and creates a new first log outside InMemory mode.

## Dependencies And Integration Points
This code depends on `logFile`, `Entry`, `valuePointer`, DB LSM `get`/`batchSet`, discard stats, Badger options, OpenTelemetry spans, `y` metrics/checksum utilities, and Ristretto `z.Closer`/histogram support. Encryption hooks route through `logFile.encryptionEnabled` and `decryptKV`.

## Risks And Edge Cases
Critical risks are partial/corrupt entry truncation, checksum mismatch handling, pointer offset overflow, log rotation races, deleting logs still needed by iterators, stale LSM versions after GC, and read-only opening when replay/truncation is required. `vlogThreshold.update` sends to a buffered channel and can block if the listener stalls. `safeRead.Entry` allocates a combined buffer and overwrites entry key/value slices with decoded data.

## Test Signals
`value_test.go` and benchmarks cover append/read round trips, checksum and partial-WAL recovery, GC rewrite correctness, iterator survival during GC, persisted discard stats, transaction-bit stripping, write validation overflow, and first-vlog ID expectations.
