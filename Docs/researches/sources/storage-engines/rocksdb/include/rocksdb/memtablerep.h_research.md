# Research: sources/storage-engines/rocksdb/include/rocksdb/memtablerep.h

## Purpose

`memtablerep.h` defines the pluggable in-memory data-structure contract backing RocksDB memtables. It allows skip list, vector, hash skip list, hash linked list, and custom representations to store encoded internal keys and values before flush.

## Important APIs, Types, and Functions

Core types are `KeyHandle`, `MemTableRep`, nested `MemTableRep::KeyComparator`, nested `MemTableRep::Iterator`, and `MemTableRepFactory`. `MemTableRep` exposes allocation, insertion variants with optional hints and concurrent insertion, `BatchPostProcess`, `Contains`, `MarkReadOnly`, `MarkFlushed`, point lookup `Get`, validation lookup `GetAndValidate`, sorted-key `MultiGet`, approximate entry count, random sampling, memory usage, iterators, dynamic-prefix iterators, and feature predicates for merge operators and snapshots. Factories include `SkipListFactory`, `VectorRepFactory`, `NewHashSkipListRepFactory`, and `NewHashLinkListRepFactory`.

## Control Flow

MemTable code asks the configured `MemTableRepFactory` to create a representation with a comparator, allocator, prefix extractor, logger, and optionally column-family id. Writers allocate encoded entries and insert them; concurrent insert-capable reps use `InsertConcurrently` and `BatchPostProcess`. Readers call `Contains`, `Get`, `MultiGet`, or create iterators and seek through encoded internal keys. When a mutable memtable stops accepting writes, RocksDB calls `MarkReadOnly`; after stable flush, it calls `MarkFlushed`.

## State and Persistence Behavior

The representation owns in-memory entries allocated through an `Allocator`; entries are never deleted individually. It is mutable until read-only, then flushed to SST by higher layers. Implementations may maintain skip-list nodes, vectors, hash buckets, thread-local buffers, hints, and memory outside the allocator reported through `ApproximateMemoryUsage`. `MarkFlushed` is a lifecycle notification, not persistence itself.

## Dependencies and Integration Points

The header depends on `Customizable` and `Slice`, and forward-declares allocator, arena, lookup key, prefix transform, logger, and DB options. Built-in factory parsing is implemented in `table/plain/plain_table_factory.cc` and exposed through options as `memtable_factory`. Integration points include write path memtables, options parsing, Java samples, custom factory tests, vector and prefix hash modes, and validation paths that detect key ordering corruption.

## Risks and Edge Cases

The encoded key format is part of the API contract through `KeyComparator::decode_key`; custom reps must preserve it. Duplicate handling is optional and must match `CanHandleDuplicatedKey`. Concurrent insertion support must be accurately advertised. Prefix-hash reps are workload-specific and can make cross-prefix iteration expensive. Iterator allocation in an arena requires callers to destroy the iterator manually without `delete`. Validation APIs can return `NotSupported`, so callers must have fallback or feature checks.

## Test Signals

Signals include options tests for `skip_list`, `vector`, `prefix_hash`, and `hash_linkedlist` parsing; custom factory loading tests; memtable read/write, concurrent write, duplicate-key, merge, snapshot, iterator ordering, and corruption-validation tests; plus db_stress exercising configured memtable factories. Assertions should cover sorted iteration, successful lookups, approximate memory accounting, no duplicate insertion when advertised, and no long blocking in `MarkFlushed`.
