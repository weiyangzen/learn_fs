# sources/storage-engines/rocksdb/utilities/object_registry_test.cc

## Purpose
This file tests `ObjectLibrary`, `ObjectRegistry`, managed objects, plugin registration, and `PatternEntry` matching semantics.

## Important APIs, types, and functions
Static factories `test_reg_a` and `test_reg_b` register Env factories in the default library. `WrappedEnv` gives owned wrappers around `Env::Default()`.

`RegisterTestUnguarded()` registers one static/unguarded and one owned/guarded Env factory. `MyCustomizable` is a test `Customizable` with type, name, and id behavior.

Registry tests cover `NewStaticObject`, `NewUniqueObject`, `NewSharedObject`, `NewObject`, local libraries, parent registries, factory counts/names/types, weak managed objects, alternate managed names, multiple managed classes, parent managed-object conflict behavior, `GetOrCreateManagedObject`, and `RegisterPlugin`.

Pattern tests cover simple entries, required/optional separator patterns, zero-or-more suffixes, numeric and decimal matches, individual ids of the form `AA@...#...`, alternate names, multiple separators/numbers, suffix plus pattern combinations, and alternate names with patterns.

## Control flow
Tests build registries and libraries, register factories, then request objects under different ownership APIs to verify whether guarded factories are accepted for unique/shared and rejected for static, while unguarded factories have the opposite behavior. Managed object tests reset shared pointers to verify weak registry entries expire.

Pattern tests construct `PatternEntry` objects incrementally and assert exact match truth tables.

## State and persistence behavior
The default object library is mutated by static registration before tests run and persists process-wide. Test-local registries and libraries are heap objects. Managed object entries are weak and disappear when test-held shared pointers reset.

## Dependencies and integration points
The file depends on `rocksdb/utilities/object_registry.h`, `rocksdb/convenience.h`, `Customizable`, Env wrappers, and the RocksDB test harness.

## Risks and edge cases
Because default-library factories are static globals, test order and global registry pollution can affect later tests if names collide. Some tests intentionally count failed factory creations that still increment counters before ownership rejection. Pattern matching coverage is broad but still does not cover every possible empty separator or malformed UTF/non-ASCII input case.

## Test signals
This is strong direct coverage for object registry behavior and pattern matching. It validates important lifetime semantics for weak managed objects and ownership mode safety.
