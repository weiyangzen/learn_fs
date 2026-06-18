<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/SstFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/SstFileInfo.java

Purpose: Base value object describing an SST file by extensionless file name, key range, and column family.

Important APIs/types/functions: Constructors accept explicit fields or RocksDB `LiveFileMetaData`. The metadata constructor strips `.sst` via `FilenameUtils.getBaseName` and decodes smallest/largest keys and column family bytes. Methods expose fields, equality/hash code, `copyObject`, `toString`, and `getFilePath(Path)` which appends `.sst`.

Control flow and state: Instances are immutable. Equality requires all four metadata fields to match, so file name alone is not considered sufficient identity.

Dependencies and integration points: Extended by `CompactionFileInfo` and `CompactionNode`; used in snapshot version maps, diff results, and path lookup for backup/source SSTs.

Risks: Key ranges are decoded as strings, so binary key encodings must be compatible with the string conversion used elsewhere. Equality including key range and column family means the same file name with changed metadata is treated as different in set comparison.

Test signals: `TestSstFileInfo` verifies conversion from mocked `LiveFileMetaData`, including base-name extraction and byte-to-string decoding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/SstFileInfo.java -->
