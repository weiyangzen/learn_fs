# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalData.java

Purpose: `OmSnapshotLocalData` is the in-memory and YAML-serializable model of per-snapshot local metadata used by snapshot SST filtering/defragmentation. It records snapshot identity, versioned SST file metadata, checksum, defrag state, previous snapshot linkage, purge transaction info, and RocksDB sequence number.

Important APIs and types: constructors create initial version `0` from RocksDB `LiveFileMetaData` or deep-copy an existing object. Getters/setters expose defrag flags, last defrag time, previous snapshot ID, transaction info, DB transaction sequence, version, and checksum. `addVersionSSTFileInfos` increments the version and stores a `VersionMeta`; `removeVersionSSTFileInfos` deletes a version. `VersionMeta` stores previous snapshot version and immutable `SstFileInfo` list and implements deep copy/equality.

Control flow: checksum computation sets a dummy 64-byte checksum, dumps the object through SnakeYAML, and computes SHA-256 of the dump. `LinkedHashMap` is used for deterministic version ordering and checksum stability.

State and persistence: persisted by YAML helpers, not RocksDB tables directly. The checksum protects serialized YAML content excluding its final checksum value.

Dependencies and integration points: used by snapshot local data YAML read/write code, snapshot defrag services, RocksDB live-file metadata, `TransactionInfo`, and checksum validation via `WithChecksum`.

Risks: deterministic serialization is required for stable checksums; changing field order, YAML representers, or map type can invalidate checksums. Copy constructor shares immutable/simple objects like UUID and `TransactionInfo`, which is acceptable if those remain immutable.

Test signals: cover checksum round trips, version ordering, add/remove version behavior, deep copy of `VersionMeta` and SST lists, default version zero creation, previous snapshot null handling, and equality/hashCode for `VersionMeta`.
