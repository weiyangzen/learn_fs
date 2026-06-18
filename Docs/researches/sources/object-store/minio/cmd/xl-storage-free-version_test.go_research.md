# sources/object-store/minio/cmd/xl-storage-free-version_test.go

## Purpose
This test file validates the free-version lifecycle for tiered object content. It confirms that internal cleanup versions are created only for transitioned content, hidden or shown appropriately, and removable by scanner-like flows.

## Important APIs, Types, and Functions
`listFreeVersions` is a test helper that calls `xlMetaV2.ListVersions` and filters `FileInfo.TierFreeVersion()`. `TestFreeVersion` exercises `AddVersion`, `DeleteVersion`, `AddFreeVersion`, `ToFileInfo`, `listFreeVersions`, `SetTierFreeVersionID`, and tier metadata fields. `TestSkipFreeVersion` directly exercises `xlMetaV2Object.InitFreeVersion` and `FileInfo.SetSkipTierFreeVersion`.

## Control Flow
`TestFreeVersion` creates a local version and a null version, marks the null version as transitioned, deletes/overwrites/removes it with specific free-version IDs, and asserts the stack contains two free-versions plus one non-free version. It then checks three read cases: including free versions while a non-free version exists returns the non-free latest version; including free versions after deleting the non-free version returns the latest free-version; excluding free versions when only free-versions remain returns `errFileNotFound`. Finally it deletes each free-version and verifies none remain, and verifies `AddFreeVersion` is a no-op for non-tiered content.

`TestSkipFreeVersion` constructs an object with transition metadata and verifies `InitFreeVersion` creates a free-version by default, then sets the skip flag and verifies no free-version is created.

## State and Persistence Behavior
The tests encode the intended internal-state model: free-versions are persisted as delete-marker versions, have their own UUIDs distinct from user-visible versions, preserve tier metadata, and should not count as normal versions when user data exists. The scanner can later delete free-version records by version ID through the same metadata delete mechanism.

## Dependencies and Integration Points
The tests depend on lifecycle `TransitionComplete`, UUID generation, `FileInfo` tier helper methods, erasure info setup, and v2 metadata mutation/listing APIs. They mirror production flows in erasure object overwrite/delete and lifecycle scanner cleanup.

## Risks and Edge Cases
The tests focus on a single object stack and do not cover corrupted tier metadata, invalid free-version UUID panic behavior, or concurrent updates across disks. They do, however, cover the most important visibility invariant: internal free cleanup versions must not appear as normal object versions.

## Test Signals
Passing tests indicate free-version creation, hiding, explicit inclusion, no-op non-tiered behavior, and skip semantics are intact. Failures usually point to lifecycle tier cleanup leaks or accidental exposure of internal versions.
