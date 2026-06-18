
# sources/sync-backup/restic/internal/restic/ids.go

Purpose: defines `IDs`, a sortable slice of `ID` values with compact string formatting.

It implements `Len`, `Less`, `Swap`, and `String`. Sorting compares raw ID bytes via string conversion. `String` preallocates a builder and renders each ID as its 8-character hex prefix inside brackets, separated by spaces.

State is in-memory value lists, commonly used for index IDs, obsolete files, or diagnostics. Integration points include repair index obsolete lists, backend listing results, and user/log output. Risks include compact strings not being canonical IDs and raw-byte ordering differing only by ID bytes, which is intended. `ids_test.go` checks formatting and duplicate preservation.
