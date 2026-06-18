# sources/storage-engines/rocksdb/utilities/options/options_util.cc

## Purpose
This file implements utilities for loading RocksDB options from OPTIONS files, finding the latest OPTIONS file in a DB directory, loading the latest options, and checking current option compatibility against persisted options.

## Important APIs, types, and functions
`LoadOptionsFromFile()` uses `RocksDBOptionsParser::Parse()` with the filesystem from `config_options.env`, copies parsed DB options, builds `ColumnFamilyDescriptor` entries from parsed CF names/options, and optionally injects a supplied shared block cache into any parsed block-based table factory.

`GetLatestOptionsFileName()` lists DB directory children through `Env`, parses filenames with `ParseFileName()`, selects the `kOptionsFile` with the highest timestamp, and returns `NotFound(PathNotFound)` when the directory is missing or contains no options file.

`LoadLatestOptions()` combines latest-file lookup and file parsing.

`CheckOptionsCompatibility()` finds the latest options file, converts supplied CF descriptors into separate name/options vectors, and calls `RocksDBOptionsParser::VerifyRocksDBOptionsFromFile()`.

## Control flow
All operations are synchronous. Latest-file selection is a linear scan. Compatibility verification delegates to the parser, using the filesystem from `config_options.env`.

## State and persistence behavior
The utilities read OPTIONS files but do not mutate DB state. When a cache pointer is supplied, loaded CF descriptors are modified in memory so block-based table factories share that cache.

## Dependencies and integration points
It depends on filename parsing, `options/options_parser.h`, RocksDB convenience/options APIs, and block-based table factory options. It integrates DB open/reopen flows with persisted options files and compatibility checks.

## Risks and edge cases
`LoadOptionsFromFile()` assumes `config_options.env` is non-null. Cache injection only affects table factories whose options are `BlockBasedTableOptions`; other table factories are ignored. Latest-file selection by numeric timestamp ignores malformed or non-options files. Path joining uses `dbpath + "/" + options_file_name`.

## Test signals
`options_util_test.cc` covers save/load, cache injection, compatibility sanity, missing/bad/latest options files, future-version unknown options handling, directory renames, and WAL directory normalization.
