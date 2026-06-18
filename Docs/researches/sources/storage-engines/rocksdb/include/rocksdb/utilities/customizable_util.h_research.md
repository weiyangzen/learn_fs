# sources/storage-engines/rocksdb/include/rocksdb/utilities/customizable_util.h

## Purpose
Template convenience layer for creating RocksDB `Customizable` objects from registry ids, option maps, or serialized option strings. It is primarily used by `CreateFromString` implementations for extension types.

## Important APIs, Types, And Functions
Key helpers are `NewSharedObject`, `LoadSharedObject`, `NewManagedObject`, `LoadManagedObject`, `NewUniqueObject`, `LoadUniqueObject`, `NewStaticObject`, and `LoadStaticObject`. They cover shared, managed registry-cached, unique, and raw/static pointer ownership models.

## Control Flow, State, And Persistence
`Load*` parses strings through `Customizable::GetOptionsMap`, then `New*` looks up factories in `ConfigOptions::registry`, creates an object, and configures it with `Customizable::ConfigureNewObject` or `ConfigureFromMap`. Empty id plus empty options resets shared/unique/static outputs; managed objects require an id and reuse an existing object if one is already in the registry. State changes are in output pointers and registry-managed weak/shared objects only; there is no durable persistence.

## Dependencies And Integration Points
Depends on `rocksdb/customizable.h`, `rocksdb/convenience.h`, `Status`, and `ObjectRegistry`. It integrates with options parsing, plugin registration, configurable object serialization, and factory-backed extension points such as cache/table/comparator/env implementations.

## Risks And Edge Cases
`ignore_unsupported_options` can convert unknown factory ids into success. Managed objects are configured only on first creation, so later option maps for the same id are ignored. Static/raw creation requires an unguarded factory object, while shared/unique creation requires guarded ownership. Empty ids with non-empty maps return `NotSupported`.

## Test Signals
Validate id-only strings, braced maps, reset behavior, managed reuse, unsupported-id ignore behavior, unknown-option handling, and ownership mismatch errors.
