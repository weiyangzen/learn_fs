# sources/sync-backup/kopia/tests/end_to_end_test/maintenance_test.go

## Purpose
Format-specific test for full maintenance behavior, safety margins, and blob cleanup after snapshot deletion.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestFullMaintenance` uses `cli.MaintenanceInfo` and `snapshot.Manifest`.

## Control Flow
The test creates a repo with repository logs disabled, reads maintenance info, snapshots shared data with JSON output, sleeps to separate deletion time, deletes the snapshot, records data blobs, runs full maintenance with default safety and expects no blob reduction, then runs full maintenance with `--safety=none` and expects blob count to drop to at most two.

## State and Persistence Behavior
Creates and deletes snapshot manifests and data blobs, then maintenance rewrites/removes repository storage. Repository logs are disabled to keep blob counts predictable.

## Dependencies and Integration Points
Exercises maintenance info/run, snapshot create/delete, blob listing, content listing, and retention safety behavior.

## Risks
Blob-count expectations are sensitive to format changes. Sleep is required because create/delete in the same second can affect safety logic.

## Test Signals
Confirms default maintenance safety preserves recently deleted data, explicit no-safety removes unreferenced blobs, and repository remains listable afterward.
