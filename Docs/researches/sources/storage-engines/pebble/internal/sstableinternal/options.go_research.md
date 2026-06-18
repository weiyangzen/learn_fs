# sources/storage-engines/pebble/internal/sstableinternal/options.go

## Purpose
This file defines internal-only option structs shared with Pebble sstable readers and writers. It carries cache integration and test-only key-order-check disabling through package boundaries that external users cannot set directly.

## Important APIs, Types, and Functions
`CacheOptions` contains an optional `*cache.Handle` and the `base.DiskFileNum` needed for cache identity. `ReaderOptions` currently embeds `CacheOpts`. `WriterOptions` embeds `CacheOpts` and adds `DisableKeyOrderChecks`, intended only for constructing invalid test sstables.

## Control Flow and State
There is no control flow. The structs transport configuration into sstable internals. Cache state itself is owned by `cache.Handle`, not this package.

## Dependencies and Integration
The file depends on Pebble `base` and `cache`. It creates an internal extension point for the public `sstable.ReaderOptions` and `sstable.WriterOptions` without exposing fields outside Pebble.

## Risks and Edge Cases
When `CacheHandle` is non-nil, `FileNum` must be set consistently; the struct comments state this but the type does not enforce it. `DisableKeyOrderChecks` is dangerous outside controlled tests because it permits invalid table construction.

## Test Signals
No direct tests are included. Validation occurs through sstable reader/writer tests and test tooling that creates malformed sstables.
