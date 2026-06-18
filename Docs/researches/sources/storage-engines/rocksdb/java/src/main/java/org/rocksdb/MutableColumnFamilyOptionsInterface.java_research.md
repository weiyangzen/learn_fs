# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptionsInterface.java research

## Purpose

`MutableColumnFamilyOptionsInterface` defines the public fluent API for the core dynamically changeable column-family options. It extends `AdvancedMutableColumnFamilyOptionsInterface` to combine common and advanced mutable CF settings.

## Important APIs and types

The interface is generic, returning `T` from setters to support fluent use by both full `Options` and mutable-options builders. It declares write buffer size, automatic compaction disablement, level-0 compaction trigger, max compaction bytes, max bytes for level base, and compression type accessors.

## Control flow

There is no implementation. Implementers map these calls either to immediate native setter/getter calls (`Options`) or to deferred key/value storage (`MutableColumnFamilyOptionsBuilder`).

## State and persistence behavior

The interface owns no state. Implementations can either mutate native options immediately or create serialized mutable-option payloads. The documented options affect in-memory buffering, background compaction, and future SST compression/layout.

## Dependencies and integration points

It depends on `CompressionType` and the advanced mutable CF interface. It is a shared contract between live `Options`, parsed mutable options, and `RocksDB.setOptions` call sites.

## Risks and test signals

The risk is contract divergence: implementers must preserve method names, return types, and semantics. Tests should ensure `Options` and `MutableColumnFamilyOptionsBuilder` both implement the same calls and that generated mutable options apply successfully to an open column family.
