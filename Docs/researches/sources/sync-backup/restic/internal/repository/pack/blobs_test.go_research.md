
# sources/sync-backup/restic/internal/repository/pack/blobs_test.go

Purpose: tests the `Blobs.Sort` helper.

`TestBlobsSort` constructs three blobs with offsets 100, 0, and 50, calls `Sort`, and asserts ascending offsets. `TestBlobsSortNilSlice` calls `Sort` on a nil `Blobs` slice to ensure the helper is safe for empty inputs.

The test has no backend or persistence state. Its integration value is defensive: many repository streaming paths sort blob lists before range reads, and nil or empty inputs can appear in repack and selective load paths. The main risk covered is regressions in offset ordering that could lead to corrupted pack reads or overlap detection failures.
