# sources/storage-engines/leveldb/db/repair.cc

Purpose: implements `RepairDB`, a best-effort salvage path that reconstructs a descriptor from surviving LevelDB log and table files. It converts logs into tables, scans tables for metadata, archives unusable files, and writes a fresh MANIFEST with all recovered tables placed at level 0.

Important APIs and types: internal `Repairer`, `TableInfo`, `Run`, `FindFiles`, `ConvertLogFilesToTables`, `ConvertLogToTable`, `ExtractMetaData`, `ScanTable`, `RepairTable`, `WriteDescriptor`, `ArchiveFile`, and public `RepairDB`. It uses `FileMetaData`, `VersionEdit`, `TableCache`, `MemTable`, `BuildTable`, `log::Reader`, and `log::Writer`.

Control flow: `Run` lists DB children, records manifests/logs/tables, converts each log to a memtable and then a new table, scans all table numbers to discover smallest/largest internal keys and max sequence numbers, then writes a temporary descriptor. Successful descriptor writing archives old manifests, renames the temp file to `MANIFEST-000001`, and updates `CURRENT`.

State and persistence behavior: repair intentionally discards old compaction layout and adds every recovered table as a level-0 file. It sets log number to 0, next file to one past the largest allocated or generated number, and last sequence to the maximum sequence seen while scanning tables. Logs and obsolete/corrupt tables are moved under `lost/`, preserving evidence while removing them from active metadata.

Dependencies and integration: tightly coupled to DB file naming, internal key parsing, table iteration, batch insertion into memtables, and table building. `SanitizeOptions` may create owned defaults for logging and cache, tracked by `owns_info_log_` and `owns_cache_`.

Risks and edge cases: the log reader is constructed with checksum verification disabled despite a comment claiming checksumming, so corrupt physical log records may be handled according to the reader's non-checksummed semantics. Repaired DBs may lose data or resurrect overwritten state because all table files are reintroduced at level 0 with broad overlap. `RepairTable` only copies entries it can iterate, so partially corrupt tables may be truncated to readable records.

Test signals: this file is indirectly covered by DB repair tests elsewhere and by public `leveldb_repair_db` bindings. The code logs recovered file counts and bytes, but the success status does not guarantee full data preservation.
