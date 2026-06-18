# sources/storage-engines/rocksdb/utilities/object_registry.cc

## Purpose
This file implements RocksDB's object registry and object library mechanics: matching URI/name patterns to factories, maintaining local and parent registries, managing weakly referenced named objects, registering plugins, and dumping registered factory metadata.

## Important APIs, types, and functions
`MatchesInteger()` and `MatchesDecimal()` validate numeric pattern spans, allowing leading `-` and requiring at least one digit. `ObjectLibrary::PatternEntry::MatchSeparatorAt()` and `MatchesTarget()` implement pattern matching over base names, separators, suffixes, integer/decimal quantifiers, exact matches, zero-or-more matches, optional base names, and alternate names.

`ObjectLibrary` methods include `GetFactoryCount()`, `GetFactoryNames()`, `GetFactoryTypes()`, `Dump()`, and `Default()`. The default library is a static avoid-destruction singleton.

`ObjectRegistry` constructors attach libraries and builtins. `Default()` and `NewInstance()` create singleton/default-parented registries. `SetManagedObject()`, `GetManagedObject()`, and `ListManagedObjects()` manage weak references keyed by type/id and delegate to parents. Factory count/name/type methods aggregate parent plus local libraries. `Dump()` logs plugins and libraries. `RegisterPlugin()` records plugin name and invokes a registrar against a newly added library.

## Control flow
Pattern matching first tries the primary name, then alternate names. For patterned names, it checks prefix, walks separators in order, changes the matching mode according to each separator's quantifier, and validates the remaining tail.

Registry lookup generally checks current state first for managed objects, then parent. Factory metadata counts parent first then local libraries. Plugins append to `plugins_`, create a named library, and invoke the registration callback.

## State and persistence behavior
Registry state is in-memory process state. `ObjectLibrary::Default()` and `ObjectRegistry::Default()` are long-lived singletons. Managed objects are stored as `weak_ptr`, so objects disappear from registry results once external shared ownership is gone. Libraries and plugin lists are owned by registries.

## Dependencies and integration points
It depends on `rocksdb/utilities/object_registry.h`, logging, `Customizable`, `Env`, and string utilities. It underpins options parsing, `LoadSharedObject`, merge operator creation, and configurable RocksDB components.

## Risks and edge cases
Global singleton registration can leak state across tests. Managed object keys use type/id strings, so collisions or inconsistent `GetId()` implementations matter. Pattern matching is hand-rolled and subtle around empty separators, decimal syntax such as `.1`, and optional names. Weak managed objects require callers to hold shared ownership elsewhere.

## Test signals
`object_registry_test.cc` covers factory ownership modes, local/default/parent registry behavior, managed object lifetimes and aliases, plugin registration, factory metadata counts, and many pattern matching cases.
