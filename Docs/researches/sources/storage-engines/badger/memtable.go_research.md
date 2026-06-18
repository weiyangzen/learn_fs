<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/memtable.go -->
# sources/storage-engines/badger/memtable.go

## Purpose
This file implements Badger memtables and their write-ahead log files. A memtable combines an in-memory skiplist with an mmap-backed WAL that can be replayed after a crash and deleted when the memtable is flushed.

## Important APIs, Types, And Functions
`memTable` stores a `skl.Skiplist`, `logFile`, max version, options, and reusable encode buffer. DB-level functions include `openMemTables`, `openMemTable`, `newMemTable`, and `mtFilePath`. Memtable methods include `SyncWAL`, `isFull`, `Put`, `UpdateSkipList`, `IncrRef`, `DecrRef`, and `replayFunction`.

`logFile` wraps a `z.MmapFile` with locking, fid/path, size/write offsets, encryption key material, registry, and options. Core methods are `Truncate`, `encodeEntry`, `writeEntry`, `decodeEntry`, `decryptKV`, `keyID`, `encryptionEnabled`, `read`, `generateIV`, `doneWriting`, `iterate`, `zeroNextEntry`, `open`, and `bootstrap`.

## Control Flow
Startup scans `*.mem` files, sorts by fid, opens each WAL read-write or read-only, replays valid entries into a skiplist, truncates to the valid end in writable mode, and appends non-empty replayed memtables to `db.imm`. New memtables create/open the next numbered WAL with size `2*MemTableSize`. `Put` encodes the entry into WAL first, skips inserting finish markers into the skiplist, then inserts normal entries and updates `maxVersion`.

WAL iteration starts after the fixed header, decodes entries through `safeRead`, tracks multi-entry transactions until a matching `bitFinTxn`, calls a callback only for complete transactions, and stops at EOF, zero entry, truncation marker, or incomplete transaction. `doneWriting` optionally syncs, locks the mmap/file, truncates to the written offset, and leaves the file open read-write.

## State And Persistence Behavior
WAL files have a header containing an 8-byte data-key ID and 12-byte base IV. Entry records contain encoded header, key, value, and CRC32C; key/value bytes are encrypted with AES CTR-derived XOR when a data key is present. `zeroNextEntry` writes zeros after each WAL write so crash recovery can detect the end. `UpdateSkipList` truncates only in writable mode and returns `ErrTruncateNeeded` in read-only mode if dirty trailing bytes exist. Skiplist reference release deletes the WAL file after flush.

## Dependencies And Integration Points
The file depends on `skl`, `Entry`, value-pointer encoding, `safeRead`, value-log constants such as `vlogHeaderSize`, encryption key registry, `pb.DataKey`, mmap helpers from `z`, metrics in `y`, and DB fields `imm`/`nextMemFid`. It is the bridge between the write path, recovery, L0 flush pipeline, encryption, and value-log pointer reads.

## Risks And Edge Cases
Mmap truncation/remap needs locking to avoid readers touching invalid memory. WAL replay must distinguish complete transactions from partially written batches. A read-only DB with dirty WAL tail fails because it cannot truncate. The arena/skiplist size and WAL size thresholds can diverge; `isFull` considers both. The `read` method checks actual `lf.size` to avoid returning bytes past a concurrent drop/truncate.

## Test Signals
The listed subset does not include dedicated memtable tests, but managed/drop/reopen tests exercise WAL replay and truncation indirectly. Metrics tests observe writes into L0. Failure signals include lost data after reopen, read-only truncate errors, corrupted transaction replay, or WAL deletion/refcount leaks after flush.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/memtable.go -->
