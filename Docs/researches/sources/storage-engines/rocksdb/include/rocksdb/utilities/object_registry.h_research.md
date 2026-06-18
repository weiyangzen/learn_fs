# sources/storage-engines/rocksdb/include/rocksdb/utilities/object_registry.h

## Purpose
Runtime factory and managed-object registry for RocksDB extension/configuration objects. It supports name/pattern-based object creation, plugin libraries, and reusable named objects.

## Important APIs, Types, And Functions
Defines `FactoryFunc`, `RegistrarFunc`, `ConfigureFunc`, `ObjectLibrary`, `ObjectLibrary::PatternEntry`, and `ObjectRegistry`. Important registry methods include library addition, `NewObject`, `NewUniqueObject`, `NewSharedObject`, `NewStaticObject`, managed-object set/get/list, `GetOrCreateManagedObject`, plugin registration, factory introspection, and `Dump`.

## Control Flow, State, And Persistence
Libraries store factories by customizable type. Factory lookup searches local libraries in reverse addition order, then parent registries. Object creation invokes the factory and validates ownership mode. Managed objects are held in weak maps by `type://id`; parent managed objects are preferred. State is in-memory only.

## Dependencies And Integration Points
Depends on `Status`, `Customizable`, `Logger`, mutexes, and STL containers. It integrates with `ConfigOptions::registry`, options-file parsing, plugin loading, and customizable extension points.

## Risks And Edge Cases
Pattern matching is intentionally limited and not full regex. Later libraries override earlier ones. Ownership mismatch between factory result and requested pointer type yields errors. Managed objects can expire because storage is weak, and reused managed ids are not reconfigured.

## Test Signals
Cover pattern suffix/separator/number/alt matching, parent lookup, library precedence, plugin registration, factory failures, ownership mismatch, managed object reuse/expiration, and concurrent access.
