# sources/storage-engines/pebble/metamorphic/key_manager_test.go

## Purpose
`key_manager_test.go` validates key-manager bookkeeping, single-delete invariants, operation key extraction, prior-run key seeding, and key-generator in-range behavior.

## Important Tests and Helpers
- `TestKeyManager_AddKey` verifies sorted global keys, prefix extraction through the key format, duplicate suppression, and `prefixExists`.
- `mustParseObjID` and `printKeys` support datadriven commands.
- `TestKeyManager` runs `testdata/key_manager` commands for reset, add-new-key, bounds, keys, singledel-keys, conflicts, and parsed op updates.
- `TestOpWrittenKeys` iterates over `methods` constructors to ensure every operation type is accepted by `opWrittenKeys`.
- `TestLoadPrecedingKeys` generates ops, loads them into a new manager/key generator, and checks previous keys/prefixes are represented.
- `TestGenerateRandKeyInRange` tests all known key formats by generating random ranges with distinct prefixes and asserting generated keys fall within `[start,end)`.

## Control Flow and State
The datadriven test mutates a shared `keyManager` across commands until `reset`. For `op` commands, it parses formatted operation text with undefined objects allowed, updates the key manager, and echoes the formatted operation. This exercises the same parse/update path used when seeding cross-version runs from prior ops.

## Dependencies and Integration Points
The file uses `datadriven`, `crstrings.LinesSeq`, Pebble key ranges, `randvar`, parser support, and `knownKeyFormats`. It is tightly coupled to method registration through `methods`, because `TestOpWrittenKeys` is intended to fail when a new operation lacks `opWrittenKeys` handling.

## Risks and Edge Cases
- Datadriven coverage is only as complete as `testdata/key_manager`.
- `TestLoadPrecedingKeys` uses subset checks because original generation may create keys that never appear in operations and may not sample distribution maxima.
- Range generation tests avoid equal prefixes because `RandKeyInRange` requires distinct split prefixes.

## Test Signals
Passing tests signal that the generator can safely choose single deletes, that cross-version runs can import previous interesting keys, and that new op types are not silently omitted from preceding-key discovery.
