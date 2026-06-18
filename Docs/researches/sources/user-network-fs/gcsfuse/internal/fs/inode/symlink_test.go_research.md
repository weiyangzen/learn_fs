# sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_test.go

Purpose: external-package tests for the exported symlink inode surface and symlink detection helper. It verifies compatibility metadata, public attributes, size update behavior, and source-object reconstruction.

Important tests: `TestIsSymLinkWhenMetadataKeyIsPresent`, `TestIsSymLinkWhenMetadataKeyIsNotPresent`, `TestIsSymLinkWhenStandardMetadataKeyIsPresent`, `TestIsSymLinkWhenStandardMetadataKeyIsFalse`, and `TestIsSymLinkForNilObject` cover `IsSymlink` recognition rules. `TestAttributes` builds a legacy symlink inode and asserts stable attributes for both `clobberedCheck` values, including `Nlink`, `Uid`, `Gid`, and `Mode`. `TestUpdateSize` checks that `UpdateSize` changes `SourceGeneration().Size`. `TestSource` creates a standard symlink object, builds an inode, and verifies `Source()` mirrors name, generation, metageneration, size, metadata, and update time.

Control flow and state: setup creates a fake bucket wrapped in `gcsx.SyncerBucket`. Tests generally construct `gcs.MinObject` records directly for legacy symlinks and use `storageutil.CreateObject` for the standard symlink source test. State is confined to fake bucket objects and inode-local cached metadata.

Dependencies and integration: uses ogletest, fake storage, `storageutil`, `fuseops`, and the public `inode` package. It complements `symlink_internal_test.go` by checking the package boundary expected by filesystem code.

Risks and coverage gaps: the external tests still expect `CreateLink` legacy metadata semantics elsewhere in `local_modifications_test.go`, while `symlink.go` now supports standard content-backed symlinks. This mixed model may be intentional for backward compatibility but is a migration-sensitive area. These tests do not validate `Target()` for standard symlinks except indirectly through constructor success in other tests.

Test signals: failures identify breaks in public symlink detection semantics, inode attribute caching, generation size bookkeeping, or source-object reconstruction.
