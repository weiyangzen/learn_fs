# sources/sync-backup/syncthing/lib/structutil/structutil_test.go

Purpose: validates default tag parsing and nil-composite filling.

Important tests: `TestSetDefaults` checks string, int, float, bool, and custom `Defaulter.ParseDefault`. `TestFillNillSlices` confirms nil `[]string` gets comma-split defaults while already-provided or empty non-nil slices are preserved. `TestFillNil` confirms maps, slices, channels, pointer chains, and nested structs are allocated. `TestFillNilDoesNotBulldozeSetFields` confirms existing slices/maps/channels and pointer targets are not replaced.

State and persistence: in-memory reflection mutations only.

Dependencies and integration: package-level tests access helper behavior directly.

Risks and signals: strong coverage for intended config/report shapes. No tests for deprecated skipping, unsupported-type panics, parse errors, or slices of structs recursion.
