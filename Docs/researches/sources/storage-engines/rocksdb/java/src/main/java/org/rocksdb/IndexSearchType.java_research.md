# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexSearchType.java research

## Purpose

`IndexSearchType` is a small Java enum mirroring RocksDB's block-based table index search modes. It lets Java users configure how block index entries are searched when the enum is passed through `BlockBasedTableConfig` and JNI into native table options.

## Important APIs and types

The enum values are `kBinary`, `kInterpolation`, and `kAuto`, each carrying a byte value that must match the C++ enum. `getValue()` is package-private, which keeps byte serialization inside the `org.rocksdb` binding layer rather than exposing it as a public API.

## Control flow

There is no runtime branching beyond construction and byte retrieval. Java table-option code calls `getValue()`, JNI receives the byte, and native RocksDB interprets it as the corresponding index-search strategy.

## State and persistence behavior

The only state is the immutable byte value stored in each enum constant. The selected mode affects newly configured table readers or table options, not Java-side persistence. Any durable effect comes from native RocksDB options files or SSTs written with the selected table configuration.

## Dependencies and integration points

The enum depends only on `org.rocksdb` package conventions. It integrates with block-based table configuration and native enum parity; interpolation and auto modes require compatible bytewise comparators according to the comments.

## Risks and test signals

The main risk is JNI enum drift: a byte mismatch would silently configure the wrong native mode. Tests should assert byte parity through table option round-trips or JNI option construction, and should cover rejection or behavior differences when non-bytewise comparators are used with interpolation-oriented modes.
