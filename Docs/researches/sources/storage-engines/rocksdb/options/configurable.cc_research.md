# sources/storage-engines/rocksdb/options/configurable.cc

## Purpose
`configurable.cc` implements the generic engine for RocksDB option-bearing objects. It registers option maps against object substructures, configures from strings/maps, serializes options, lists option names, prepares and validates nested options, compares objects, and parses IDs plus property maps.

## Important APIs, Types, and Functions
Core methods include `RegisterOptions`, `PrepareOptions`, `ValidateOptions`, `GetOptionsPtr`, `ConfigureFromMap`, `ConfigureOptions`, `ConfigureFromString`, `ConfigureOption`, `ParseOption`, `GetOptionString`, `ToString`, `SerializeOptions`, `GetOption`, `GetOptionNames`, `AreEquivalent`, `OptionsAreEqual`, and static `GetOptionsMap`. `ConfigurableHelper` supplies lookup, bulk/single configuration, customizable handling, serialization, listing, and equivalence.

## Control Flow
`RegisterOptions` stores a name, type map, and byte offset to the registered substructure. Later calls recover pointers with `ApplyOffset`, so copied objects still work. `ConfigureFromString` parses either a map string or class-specific syntax. `ConfigureOptions` snapshots current serialized state, applies updates with prepare disabled, invokes prepare at the end when requested, and rolls back from the snapshot on failure. `ConfigureSomeOptions` repeatedly scans remaining entries so parent object creation can precede child property updates. `ConfigureCustomizableOption` handles ID changes, nulls, nested properties, and mutable-only constraints.

## State and Persistence Behavior
Persistent state is not owned here; `options_` stores registration metadata. Serialized strings support options files, rollback snapshots, and round-trip comparison. Rollback depends on serialization being complete enough to reconstruct the previous state.

## Dependencies and Integration Points
The file depends on logging, options helpers, `Customizable`, `ObjectRegistry`, `OptionTypeInfo`, coding helpers, and string utilities. It underpins DB/CF options, table factories, caches, filters, merge operators, statistics, encryption providers, and tests.

## Risks
Offset arithmetic is unsafe if registered pointers are not subobjects of the configurable. Non-serialized fields cannot be rolled back. Mutable-only behavior through nested configurable/customizable objects is subtle. Equivalence assumes compatible registration names and type maps.

## Test Signals
`configurable_test.cc` covers parsing, rollback, nesting, structs, enum options, mutable-only mode, alias/deprecated flags, `kDontSerialize`, `kCompareNever`, null maps, prepare/validate recursion, and copied object offsets. `customizable_test.cc` stresses the customizable branch.
