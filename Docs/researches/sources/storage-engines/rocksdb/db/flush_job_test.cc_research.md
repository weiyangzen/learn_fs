# sources/storage-engines/rocksdb/db/flush_job_test.cc

Tests `FlushJob` using a lightweight `VersionSet`, mock table factory, constructed memtables, and explicit job contexts. The purpose is to verify flush metadata, output contents, atomic flush behavior, timestamp handling, and rate-limiter priority without opening a full DB for every case.

`FlushJobTestBase` writes an initial MANIFEST/CURRENT, configures column families, initializes `VersionSet`, and owns `TableCache`, `WriteBufferManager`, `WriteController`, mutex, shutdown flag, and `mock::MockTableFactory`. `FlushJobTest` uses bytewise comparison. `FlushJobTimestampTest` parameterizes paranoid file checks and UDT persistence/stripping. Helpers encode values with write time or preferred sequence number.

Most tests add memtables to `cfd->imm()`, call `PickMemTable()` and `Run()` under the mutex, then inspect returned `FileMetaData`, mock table entries, histograms, or CF state. `FlushMemtablesMultipleColumnFamilies` creates one flush job per CF with `write_manifest_=false`, then installs all results with `InstallMemtableAtomicFlushResults()`.

Covered behavior includes empty no-op flushes, non-empty key/range-tombstone/blob-index output, partial memtable selection by ID, atomic multi-CF installation, snapshot retention of older versions, write-controller mapping from normal/delayed/stopped to flush IO priority, preferred-seqno rewriting through `SeqnoToTimeMapping`, and UDT stripping/full-history-low advancement. The timestamp tests verify both returned metadata and installed L0 metadata.

Dependencies include internal manifest setup, `VersionSet::Recover`, memtable construction, mock table building, stats histograms, and write controller tokens. Risks/gaps: mempurge, fsync/manifest failure paths, table-cache eviction after failed install, blob callbacks, and fast-SST-open are not directly targeted. This file is the main direct regression signal for `flush_job.cc`/`.h`.
