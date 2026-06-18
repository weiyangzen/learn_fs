# sources/sync-backup/kopia/repo/blob/azure/azure_versioned_test.go

Purpose: integration tests for Azure blob version listing and point-in-time selection behavior.

Important APIs/types/functions: `TestGetBlobVersionsFailsWhenVersioningDisabled`, `TestGetBlobVersions`, `TestGetBlobVersionsWithDeletion`, and `putBlobs`.

Control flow: tests set up Azure storage with versioning assumptions, write multiple blob versions, invoke PIT/version helper methods, and compare version metadata ordering and visibility. Deletion tests verify delete-marker handling so a point-in-time before or after deletion yields correct existence semantics.

State and persistence behavior: real Azure blob versions are created and may remain subject to cloud retention/versioning policies. The tests depend on server-side timestamps and version IDs.

Dependencies/integration points: exercises `azPointInTimeStorage`, `getBlobVersions`, `newestAtUnlessDeleted`, and Azure SDK listing flags. Risks include environment skips, cloud ordering/timestamp precision, and cleanup complexity. These tests are the strongest signal that Azure PIT views match Kopia's expected historical-read contract.
