# sources/sync-backup/syncthing/lib/config/compression_test.go

## sources/sync-backup/syncthing/lib/config/compression_test.go

Purpose: Verifies text marshal/unmarshal behavior for `Compression`.

Important APIs/types/functions: `TestCompressionMarshal` checks `Compression.UnmarshalText` and `Compression.MarshalText`.

Control flow and state: The test iterates legacy and current strings, expecting `"true"` to map to metadata and `"false"` to never. It also expects an arbitrary unknown string to map to `CompressionMetadata`, documenting the silent fallback behavior.

Dependencies and integration: Uses the production enum only, with no external services or filesystem state.

Risks and test signals: The test locks in backwards compatibility for old XML configs and catches regressions in canonical output strings (`never`, `metadata`, `always`).
