## sources/sync-backup/kopia/internal/blobtesting/map_test.go

Purpose: validates map-backed test storage and capacity limiting.

Important APIs/types/functions: `TestMapStorage`, `TestMapStorageWithLimit`, and `verifyCapacityAndFreeSpace`.

Control flow, state, and persistence: runs the generic `VerifyStorage` contract against map storage, then tests limited storage by adding/deleting blobs and asserting free-space accounting and limit errors.

Dependencies and integration points: uses `blobtesting.VerifyStorage`, `gather.FromSlice`, and blob capacity API.

Risks and test signals: confirms test storage behaves like a provider enough for generic tests. Does not test unsupported option errors directly.
