# sources/storage-engines/rocksdb/options/customizable_test.cc

## Purpose
`customizable_test.cc` validates `Customizable` and object-registry loading. It covers synthetic custom objects, configurable fields holding unique/shared/raw custom pointers, managed identity reuse, wrapper/inner type discovery, vectors, mutable-only nested custom updates, and creation of many RocksDB plugin-style interfaces from strings.

## Important APIs, Types, and Functions
The file defines `TestCustomizable`, `ACustomizable`, `BCustomizable`, `SimpleConfigurable`, factory registration functions, `CustomizableTest`, and `LoadCustomizableTest`. It also defines mock secondary cache, statistics, flush block policy factory, slice transform, memory allocator, encryption provider/cipher, file system, table properties collector factory, SST partitioner factory, checksum generator factory, filter policy, and cache. Helper methods enumerate built-ins/plugins and verify `CreateFromString` plus `IsInstanceOf`.

## Control Flow
Early tests register local factories and configure custom pointers using `unique={id=A;int=1}`, `unique.id=A`, nested `unique.A.int=1`, and direct `unique=A` forms. They round-trip through `GetOptionString`, property parsing, and `ConfigureFromMap`. Failure tests toggle ignore flags to classify missing factories, failing factories, and bad nested options. Managed-object tests verify same-ID reuse and cleanup when shared references disappear. Loading tests attempt built-in and registered names for table factories, file systems, caches, filters, merge operators, encryption, statistics, memory allocators, and related interfaces.

## State and Persistence Behavior
The tests validate serialized identities and option strings rather than files. Empty IDs, empty values, and `nullptr` clear custom pointers. Unnamed custom objects are omitted from serialization and not recreated. Managed objects live in `ObjectRegistry` while references remain alive.

## Dependencies and Integration Points
The suite touches DB test utilities, options parsing, object registries, table factories, filters, caches, memory allocators, encryption, file systems, statistics, merge operators, compaction filters, event listeners, and block-based table options.

## Risks Covered
Coverage includes name-pattern parsing, URL-like IDs containing delimiters, missing/failing factory errors, null handling, mutable-only restrictions, serialization of named-only custom objects, `IsInstanceOf`/`CheckedCast` through wrappers, and optional plugin variability.

## Test Signals
This is a broad integration signal for the string-to-object contract. Some memory allocator expectations are environment-dependent and are conditionally tolerated when optional allocators are unsupported.
