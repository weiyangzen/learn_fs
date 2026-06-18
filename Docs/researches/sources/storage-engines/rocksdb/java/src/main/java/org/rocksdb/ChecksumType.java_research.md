# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ChecksumType.java

- **Purpose:** Enum of checksum algorithms for block-based table files.
- **Important APIs/types/functions:** Values are `kNoChecksum`, `kCRC32c`, `kxxHash`, `kxxHash64`, and `kXXH3`, mapped to byte values 0 through 4. `getValue()` exposes the native byte.
- **Control flow:** No reverse lookup in this file; users pass byte values to native code, and some callers use `ChecksumType.values()[byte]` when reconstructing config.
- **State and persistence behavior:** Stateless enum. Selection affects checksums written to new SST/table files and read-time verification compatibility.
- **Dependencies:** Used by `BlockBasedTableConfig`.
- **Integration points:** Table format configuration and native block-based table factory creation.
- **Risks:** Java enum order and byte values must stay aligned with RocksDB C++ `ChecksumType`. `kNoChecksum` is documented as not implemented yet.
- **Test signals:** Byte mapping, table creation with each supported checksum, and config round-trip from native table descriptors.
