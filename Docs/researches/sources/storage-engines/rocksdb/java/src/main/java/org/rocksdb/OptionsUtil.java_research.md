# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionsUtil.java research

## Purpose

`OptionsUtil` exposes static helpers for loading RocksDB OPTIONS files into Java `DBOptions` and `ColumnFamilyDescriptor` objects. It bridges native option-file parsing with Java option wrappers.

## Important APIs and types

`loadLatestOptions(ConfigOptions, String, DBOptions, List<ColumnFamilyDescriptor>)` loads the newest options file from a DB directory. `loadOptionsFromFile(ConfigOptions, String, DBOptions, List<ColumnFamilyDescriptor>)` loads a specified file. `getLatestOptionsFileName(String, Env)` returns the selected options file path. Private `loadTableFormatConfig(...)` reads native table-format config for each returned column-family option.

## Control flow

Public load methods call native parsing functions with config and DB option handles plus the descriptor list, then iterate descriptors and call `ColumnFamilyOptions.setFetchedTableFormatConfig(readTableFormatConfig(...))`. The class cannot be instantiated.

## State and persistence behavior

The utility owns no state. It reads persisted OPTIONS files and mutates caller-provided `DBOptions` and descriptor lists. Pointer options generally get defaults after loading, with special support for block-based table options excluding pointer sub-options such as block cache and flush-block policy.

## Dependencies and integration points

It depends on `ConfigOptions`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `Env`, `TableFormatConfig`, and native option parsing. It is used by applications that reopen DBs from generated OPTIONS files.

## Risks and test signals

Risks include incomplete pointer-option reconstruction, table factory type loss, and caller confusion about defaults that must be reattached manually. Tests should load latest and explicit OPTIONS files, verify column-family descriptors and fetched table format configs, cover missing or malformed files, and validate custom pointer options are documented as defaults.
