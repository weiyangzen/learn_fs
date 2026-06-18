# sources/storage-engines/pebble/sstable/data_test.go

## Purpose
Provides shared datadriven test helpers for building SSTables, opening readers, iterating, and rewriting suffixes across the `sstable` package tests.

## Important APIs, Types, and Functions
- `optsFromArgs` parses writer options and fills test comparer/key schema defaults.
- `runBuildMemObjCmd`, `runBuildCmd`, and `runBuildRawCmd` build SSTables in memory or object storage and return metadata/readers.
- `openReader` constructs reader options with key schemas and filter decoders.
- `runIterCmdOption`, `runIterCmdOptions`, and option helpers configure iterator test behavior.
- `runIterCmd` interprets line-oriented iterator commands and formats results.
- `runRewriteCmd` rewrites key suffixes into a new in-memory object and returns a fresh reader.

## Control Flow
Build helpers parse options, construct raw writers, parse test SST input, close writers, collect metadata, and open readers. `runIterCmd` maintains iterator state across commands such as seek, first/last, next/prev, bounds changes, stats, masking, and internal iterator state inspection. `runRewriteCmd` parses `from`/`to`, invokes `rewriteKeySuffixesInBlocks`, closes the old reader, and opens a new one.

## State and Persistence Behavior
Most helpers use `objstorage.MemObj`, but `runBuildRawCmd` exercises a real provider over an in-memory VFS. Iterator commands mutate iterator bounds, current KV, prefix/masking state, and optional stats. Build helpers ensure writers/readers are closed on errors.

## Dependencies and Integration Points
Used by many SSTable tests, including columnar writer tests in this subset. Depends on datadriven parsing, test key comparer/schema, blob test values, bloom/test filter decoders, object storage provider, blockkind stats, and block iterators.

## Risks and Edge Cases
Because this is shared test infrastructure, subtle formatting changes can affect many golden tests. `runIterCmd` contains test-only masking and internal-state inspection logic that must track iterator implementation changes. Error cleanup paths are important to avoid leaked readers/writers in tests.

## Test Signals
This file is itself test harness code; its value is enabling broad datadriven coverage of SSTable building, iteration, filters, stats, and rewrite behavior.
