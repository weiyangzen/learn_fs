# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptions.java research

## Purpose

`MutableDBOptions` is the Java payload for dynamically changeable database-wide options. It supports fluent construction and parsing of RocksDB-style option strings for `RocksDB.setDBOptions(...)`.

## Important APIs and types

`builder()` creates `MutableDBOptionsBuilder`; `parse(String, boolean)` uses `OptionString.Parser`. The `DBOption` enum lists supported keys and `ValueType`s, including background jobs, shutdown flush behavior, file buffering, delayed write rate, WAL size, obsolete-file deletion period, stats intervals, max open files, sync settings, compaction readahead, wakeup interval, and daily off-peak time.

## Control flow

Builder methods call typed abstract builder helpers and expose corresponding getters. `ALL_KEYS_LOOKUP` maps option names to enum keys. Parsing resolves entries against that map and either rejects or ignores unknown keys according to the caller flag.

## State and persistence behavior

The built object stores key/value strings. Applying it changes live DB-wide native state. Some options affect runtime scheduling or throttling immediately; others influence future logging, WAL management, stats persistence, or file I/O behavior.

## Dependencies and integration points

It depends on `AbstractMutableOptions`, `AbstractMutableOptionsBuilder`, `MutableOptionKey`, `OptionString`, and `MutableDBOptionsInterface`. It integrates with `RocksDB.setDBOptions(MutableDBOptions)` and mirrors the mutable subset also implemented directly by `Options`.

## Risks and test signals

Risks include incomplete key coverage, deprecated `max_background_compactions` behavior, string format changes, and Java/native value-type drift. Tests should cover parse/build round-trips, unknown-key behavior, all builder methods, native application to an open DB, and off-peak time validation in native code.
