# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptions.java research

## Purpose

`MutableColumnFamilyOptions` is the Java representation of dynamically changeable column-family options. It builds the key/value arrays consumed by `RocksDB.setOptions(...)` and parses RocksDB-style option strings into a typed builder.

## Important APIs and types

`builder()` creates `MutableColumnFamilyOptionsBuilder`; `parse(String, boolean)` parses semicolon-separated options via `OptionString.Parser`. Internal enum groups implement `MutableOptionKey`: `MemtableOption`, `CompactionOption`, `BlobOption`, and `MiscOption`. Each key declares a `ValueType`. The builder extends `AbstractMutableOptionsBuilder` and implements `MutableColumnFamilyOptionsInterface`, exposing fluent setters/getters for memtable, compaction, blob, compression, and miscellaneous options.

## Control flow

Builder methods call typed helpers such as `setLong`, `setBoolean`, `setIntArray`, and `setEnum`, which store validated values in the abstract builder. `build(keys, values)` creates the immutable `MutableColumnFamilyOptions` wrapper around string arrays. Parsing first builds `OptionString.Entry` objects, then resolves keys through `ALL_KEYS_LOOKUP`, optionally ignoring unknown keys.

## State and persistence behavior

The final object stores option keys and serialized string values, not native handles. Applying it changes live native column-family state and can influence future flushes, compactions, blob files, TTL, and write throttling. Some changes affect only future files.

## Dependencies and integration points

It depends on `AbstractMutableOptions`, `AbstractMutableOptionsBuilder`, `MutableOptionKey`, `MutableOptionValue`, `OptionString`, `CompressionType`, and `PrepopulateBlobCache`. It is consumed by `RocksDB.setOptions(ColumnFamilyHandle, MutableColumnFamilyOptions)`.

## Risks and test signals

Risks include Java key lists falling behind native mutable options, deprecated keys lingering, parse ambiguity for enum values, and typed conversions losing precision. Tests should cover parse/build round-trips, unknown-key behavior, each `ValueType`, native `setOptions` application, and getter failure for unset options if the abstract builder enforces presence.
