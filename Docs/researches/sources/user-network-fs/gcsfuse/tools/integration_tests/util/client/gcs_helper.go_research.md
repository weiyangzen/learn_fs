# sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/gcs_helper.go

## Purpose

Collects high-level GCS helper functions and constants used throughout integration tests for object creation, validation, test directory setup, unfinalized object creation, requester-pays toggling, and common file names/content.

## Important APIs, control flow, and dependencies

Constants define common file and directory names, contents, sizes, and permissions. Helpers wrap lower-level storage-client operations: `CreateImplicitDir`, `ValidateObjectNotFoundErrOnGCS`, `ValidateObjectContentsFromGCS`, `ValidateObjectChunkFromGCS`, `CloseFileAndValidateContentFromGCS`, `CreateLocalFileInTestDir`, `CreateObjectInGCSTestDir`, `CreateFinalizedObjectInGCSTestDir`, `SetupFileInTestDirectory`, `SetupTestDirectory`, `SetupUniqueTestDirectory`, `CreateNFilesInDir`, `GetCRCFromGCS`, `CreateUnfinalizedObject`, and requester-pays helpers.

## State, persistence, dependencies, and integration points

Most helpers create, delete, or inspect real GCS objects through `storage.Client`. `SetupTestDirectory` deletes existing objects with the target prefix and creates a directory marker object, using `setup.MntDir` and `setup.OnlyDirMounted` to map between mounted paths and bucket objects. `CreateUnfinalizedObject` uses appendable writer setup, writes content, closes without finalizing for zonal behavior, and sleeps for size visibility.

## Risks and test signals

Risks include fatal test termination on validation mismatches, string-matching object-not-found errors, sleeps for eventual size visibility, and helpers that assume object content fits in memory. Signals are direct content equality, expected not-found errors, CRC availability, requester-pays state changes, and clean test directories.
