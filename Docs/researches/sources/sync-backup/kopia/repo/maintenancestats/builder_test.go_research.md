# sources/sync-backup/kopia/repo/maintenancestats/builder_test.go

Purpose: verifies maintenance stats JSON wrapping and reconstruction for every supported stats type.

Important APIs/types/functions: `TestBuildExtraSuccess`, `TestBuildExtraError`, `TestBuildFromExtraSuccess`, `TestBuildFromExtraError`, and `unmarshalable`.

Control flow: table-driven cases compare exact `Extra.Kind` and JSON bytes for concrete stats, then reconstruct stats from raw extras and compare structs. Error cases cover nil stats, marshal failure, unsupported kind, and bad JSON.

State/persistence behavior: no repository state; protects the JSON payloads persisted in maintenance schedule history.

Dependencies/integration: spans all stats structs and their kind constants.

Risks/test signals: exact JSON byte comparisons catch field/tag changes. The tests document compatibility expectations for stored maintenance run extras.
