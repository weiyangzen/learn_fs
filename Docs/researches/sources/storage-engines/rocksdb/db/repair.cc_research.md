# sources/storage-engines/rocksdb/db/repair.cc

## Purpose

`repair.cc` implements best-effort RocksDB database repair. It rebuilds a usable manifest from surviving WAL and SST files without promising time-consistent recovery. The file-level comments define four phases: find files, convert logs to tables, extract table metadata, and write a new descriptor.

## Important APIs, Types, and Functions

The file-local `Repairer` owns the workflow. Important methods are `Run`, `FindFiles`, `ConvertLogFilesToTables`, `ConvertLogToTable`, `ExtractMetaData`, `ScanTable`, `AddTables`, `ArchiveFile`, `AddColumnFamily`, and `Close`. Public overloads of `RepairDB` accept `Options`, `DBOptions` plus column-family descriptors, and optional unknown-column-family options.

`TableInfo` combines `FileMetaData` with column-family id/name. Repair uses `VersionSet`, `TableCache`, `MemTable`, `ColumnFamilyMemTablesImpl`, `log::Reader`, `WriteBatchInternal`, `BuildTable`, `VersionBuilder`, and `VersionEdit`.

## Control Flow and State Behavior

`Run` locks the DB, finds files across configured DB paths and separate WAL dir, archives old manifests, creates a fresh DB descriptor via temporary `DBImpl::NewDB`, recovers the new `VersionSet`, scans existing SST metadata, converts live WAL files to tables, scans those generated tables, and finally writes table additions to the manifest.

`ConvertLogToTable` reads WAL records with checksum validation. Corrupt records are logged and skipped. Valid write batches are checked for timestamp-size consistency, inserted into per-CF memtables, and each non-empty memtable is flushed with `BuildTable` using recovery table-builder options and any memtable range tombstones.

`ScanTable` opens table properties, reconstructs unique IDs when possible, discovers/creates column families, validates column-family names, scans point keys to update file boundaries and sequence bounds, then scans range tombstones to update range boundaries. `AddTables` groups recovered tables by CF, computes the max sequence, recovers epoch numbers through a dummy `VersionStorageInfo`, and writes a `VersionEdit` adding all files, currently at level 0 after dummy recovery ordering.

## Persistence, Dependencies, and Integration

Repair mutates persistent state: it archives manifests, WALs, and unreadable SSTs into `lost/`, creates new SSTs from WAL contents, writes a new MANIFEST, updates next file number and last sequence, and unlocks the DB at close. It integrates with filesystem naming, WAL format, table cache/properties, CF options, comparators, user-defined timestamp persistence, range tombstone metadata, unique SST IDs, and epoch-number ordering.

## Risks and Test Signals

Repair is intentionally lossy. It can skip corrupt WAL records or unreadable SSTs, and it does not guarantee a point-in-time consistent DB. High-risk areas are CF option selection for unknown CFs, timestamp-size validation, range tombstone boundary reconstruction, next-file-number selection, separate WAL dirs, and preserving newest values when all recovered files land in L0. `repair_test.cc` exercises these scenarios directly.
