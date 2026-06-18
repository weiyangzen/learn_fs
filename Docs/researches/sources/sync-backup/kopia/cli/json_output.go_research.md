<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/json_output.go -->
# sources/sync-backup/kopia/cli/json_output.go

## Purpose
Defines shared JSON output flags and helpers, including streaming JSON arrays and manifest cleanup for less verbose output.

## Important APIs, Types, And Functions
Key types/functions are `jsonOutput`, `setup`, `cleanupSnapshotManifestForJSON`, `cleanupSnapshotManifestListForJSON`, `cleanupForJSON`, `jsonBytes`, `jsonIndentedBytes`, and `jsonList` methods `begin`, `end`, and `emit`.

## Control Flow
Commands call `setup` to add JSON flags. Before marshaling, manifest values are wrapped so `Stats` is omitted unless `--json-verbose` is set. `jsonList` emits an array wrapper only in JSON mode and manages separators for compact or indented output.

## State And Persistence Behavior
No repository state is changed. It stores output preferences and writer references for command lifetime.

## Dependencies And Integration Points
Integrates Kingpin flags, Go JSON encoding, snapshot manifest structs, and the internal `impossible.PanicOnError` helper.

## Risks And Edge Cases
`jsonIndentedBytes` panics on marshal errors, assuming command values are JSON-safe. Non-JSON mode `jsonList` emits nothing, so callers must handle plain output separately.

## Test Signals
Tests should cover manifest stats omission/inclusion, array formatting for zero/one/many items, indented output, and command-specific JSON consumers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/json_output.go -->
