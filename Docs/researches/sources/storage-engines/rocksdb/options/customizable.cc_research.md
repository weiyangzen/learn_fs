# sources/storage-engines/rocksdb/options/customizable.cc

## Purpose
`customizable.cc` implements the `Customizable` specialization of `Configurable`: option-bearing objects with identity strings that can be created, serialized, and compared by name through RocksDB object registries.

## Important APIs, Types, and Functions
Implemented methods are `GetOptionName`, `GenerateIndividualId`, `GetOption`, `SerializeOptions`, `AreEquivalent`, static `GetOptionsMap`, and static `ConfigureNewObject`. `GetOptionName` strips a leading `<Name>.` prefix. `GenerateIndividualId` builds a process-local ID from name, address, and process ID. `GetOption` exposes the synthetic `id` property.

## Control Flow
Serialization emits only the ID for shallow or optionless objects, or emits `id=<id>` plus detailed base configurable options. Equivalence compares IDs at nonzero sanity levels and compares child options only above loose compatibility. `GetOptionsMap` parses a value into ID and properties, and when reconfiguring an existing compatible object merges current serialized options to preserve unspecified fields.

## State and Persistence Behavior
The file defines serialized identity behavior but owns no persistence. Empty and `nullptr` values represent no object. Generated individual IDs are process/address dependent and not stable across restarts.

## Dependencies and Integration Points
It depends on options helpers, `Configurable`, `Status`, `OptionTypeInfo`, string utilities, and process ID helpers. It is used by custom RocksDB components such as table factories, filters, caches, merge operators, statistics, file systems, and encryption providers.

## Risks
Detailed-vs-shallow serialization can hide child option differences unless the caller requests sufficient depth. Merging current options ignores serialization errors. Callers must pass comparable object families into `AreEquivalent`.

## Test Signals
`customizable_test.cc` covers ID creation, serialization depth, strict/loose equivalence, null handling, prepare failures, managed IDs, wrapper chains, vectors, and many registry-backed RocksDB object types.
