# sources/object-store/minio/cmd/xl-storage-free-version.go

## Purpose
This file implements XL metadata "free-version" support. A free-version is represented as a delete marker with special internal metadata and is used to track tiered remote content that must be deleted asynchronously after an object version is overwritten or removed.

## Important APIs, Types, and Functions
`freeVersion` is the internal metadata marker key suffix. `xlMetaV2Object.InitFreeVersion(fi FileInfo)` creates a delete-marker-shaped `xlMetaV2Version` when the object has completed transition metadata and the caller did not request `SkipTierFreeVersion`. `xlMetaV2DeleteMarker.FreeVersion()` and `xlMetaV2Version.FreeVersion()` identify free-version records. `xlMetaV2.AddFreeVersion(fi FileInfo)` finds the target object version and appends the generated free-version if the version has tiered content.

## Control Flow
`InitFreeVersion` first checks the caller skip flag. It then verifies the object has `x-minio-internal-transition-status` equal to lifecycle `TransitionComplete`. If so, it parses the free-version ID stored in the `FileInfo`; invalid IDs panic because the caller has already committed to a generated internal ID. The new version is type `DeleteType`, uses the original object's modtime, records the current writer version, stores the free-version marker, and copies only tier name/object/version metadata needed by the scanner to delete remote tier content. `AddFreeVersion` parses the target version ID, scans the shallow version list for an object entry with that ID, loads it, and delegates to `InitFreeVersion`.

## State and Persistence Behavior
Free-versions persist inside the normal version stack but are hidden from normal object listing and version counts by `xlMetaV2.ToFileInfo` and `xlMetaBuf` readers unless callers explicitly include them or no non-free versions remain. The marker lives in delete-marker `MetaSys` under the reserved metadata prefix. They carry tier routing metadata, not local object data, and exist so lifecycle/scanner paths can eventually purge remote tiered objects after the user-visible version is gone.

## Dependencies and Integration Points
The file depends on `FileInfo` tier/free-version accessors, lifecycle transition constants, UUID parsing, reserved internal metadata names from the v2 metadata implementation, `globalVersionUnix`, and scanner/lifecycle integrations that request `InclFreeVersions` and enqueue free-version deletion. `DeleteVersion` in the main v2 file also calls `InitFreeVersion` when deleting transitioned object versions.

## Risks and Edge Cases
The panic on invalid tier free-version ID assumes internal callers set a valid UUID; externalizing or loosening this path would need error handling. Missing tier metadata would create a free-version with insufficient deletion routing. Creating free-versions when `SkipTierFreeVersion` is set could duplicate work during lifecycle expiry. Failing to hide free-versions from normal reads would expose internal cleanup records as object versions.

## Test Signals
`xl-storage-free-version_test.go` covers creation during overwrite/removal, listing/counting free-versions, `ToFileInfo` behavior with and without `inclFreeVers`, scanner-style deletion of free-versions, no-op behavior for non-tiered versions, and skip-flag behavior.
