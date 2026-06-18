# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/DataStore.c

## Purpose

`DataStore.c` implements metadata-file lifecycle support for the MetadataManager minifilter sample.

The file demonstrates how a filter can:

- Open or create a per-volume metadata file.
- Hold both a handle and referenced file object for that metadata file.
- Temporarily release those references before volume locks, dismounts, and PnP removal.
- Reacquire the references afterward when safe.
- Avoid deadlocks when issuing filesystem operations while holding instance-context synchronization.

The sample metadata file is `\System Volume Information\FilterMetadata.md` on the target volume.

## Main State Managed

The routines operate on `FMM_INSTANCE_CONTEXT`, especially:

- `MetadataResource`: protects metadata-related state.
- `MetadataHandle`: filter-owned metadata file handle.
- `MetadataFileObject`: referenced file object for the metadata file.
- `MetadataOpenTriggerFileObject`: volume file object that caused metadata references to be dropped.
- `INSTANCE_CONTEXT_F_METADATA_OPENED`: metadata file is open.
- `INSTANCE_CONTEXT_F_TRANSITION`: the context resource was dropped around a filter-issued filesystem operation.

## `FmmOpenMetadata`

`FmmOpenMetadata` opens or creates the metadata file for an instance.

Preconditions:

- The caller holds the instance metadata resource exclusive.
- The caller is in a critical region.
- Runs at PASSIVE_LEVEL.

Behavior:

1. Builds a full metadata filename:
   - Allocates an initial Unicode buffer sized from `FMM_DEFAULT_VOLUME_NAME_LENGTH + FMM_METADATA_FILE_NAME_LENGTH`.
   - Calls `FltGetVolumeName`.
   - If the buffer is too small, frees it, grows the length, and retries.
   - Appends `FMM_METADATA_FILE_NAME`.

2. Calls `FltCreateFile`:
   - Uses `FILE_ALL_ACCESS`.
   - Creates a system/hidden file.
   - Uses `FILE_OPEN_IF` when `CreateIfNotPresent` is true, otherwise `FILE_OPEN`.
   - Shares read access.
   - Wraps the call with `FmmBeginFileSystemOperation` and `FmmEndFileSystemOperation`.

3. If creation fails with `STATUS_OBJECT_PATH_NOT_FOUND` and creation is allowed:
   - Calls `FltCreateSystemVolumeInformationFolder`.
   - Retries `FltCreateFile` if folder creation succeeds.

4. Converts the handle into a referenced file object with `ObReferenceObjectByHandle`.

5. On success:
   - Leaves `MetadataHandle` and `MetadataFileObject` stored in the instance context.
   - Sets `INSTANCE_CONTEXT_F_METADATA_OPENED`.

6. On failure:
   - Closes any handle opened so far.
   - Dereferences any metadata file object acquired.
   - Frees the Unicode filename buffer.

The function contains sample comments where a real filter would initialize or validate metadata contents.

## `FmmCloseMetadata`

`FmmCloseMetadata` closes the filter’s metadata references.

Preconditions:

- Caller holds `MetadataResource`.
- Metadata handle and file object must both be present.

Behavior:

- Dereferences `MetadataFileObject`.
- Calls `FltClose` on `MetadataHandle`, again wrapped in `FmmBeginFileSystemOperation` and `FmmEndFileSystemOperation`.
- Clears both pointers.
- Clears `INSTANCE_CONTEXT_F_METADATA_OPENED`.

## `FmmReleaseMetadataFileReferences`

This routine is called when the filter must stop holding the metadata file open, usually because the filesystem needs exclusive volume access.

Behavior:

- Gets the instance context from the target instance.
- Acquires `MetadataResource` exclusive.
- If the context is in transition, returns `STATUS_FILE_LOCK_CONFLICT`.
- If metadata is open:
  - Calls `FmmCloseMetadata`.
  - Stores the current target file object in `MetadataOpenTriggerFileObject`.
- Releases the resource and context reference.

This function is used before volume locks, dismounts, and query remove.

## `FmmReacquireMetadataFileReferences`

This routine reopens the metadata file after a prior release.

Behavior:

- Gets the instance context.
- Acquires `MetadataResource` exclusive.
- If the context is in transition, returns `STATUS_FILE_LOCK_CONFLICT`.
- Reopens metadata only when `MetadataOpenTriggerFileObject` matches the current target file object.
- Calls `FmmOpenMetadata` with `CreateIfNotPresent = FALSE`.
- Clears `MetadataOpenTriggerFileObject` after the reopen attempt.
- Releases the resource and context reference.

This trigger-file-object check prevents unrelated volume handles from causing metadata to be reopened at the wrong time.

## `FmmSetMetadataOpenTriggerFileObject`

This routine records which volume file object should later trigger metadata reacquisition.

Behavior:

- Gets the instance context.
- Acquires `MetadataResource` exclusive.
- Refuses to modify state during `INSTANCE_CONTEXT_F_TRANSITION`.
- Asserts that any existing trigger is either null or the same file object.
- Stores `Cbd->Iopb->TargetFileObject`.

This is used after successful volume locks, including cases where lower filters may have recursively issued lock operations.

## Transition Helpers

### `FmmBeginFileSystemOperation`

Called before the filter sends filesystem I/O while holding `MetadataResource` exclusive.

Behavior:

- Asserts the context is not already in transition.
- Sets `INSTANCE_CONTEXT_F_TRANSITION`.
- Releases `MetadataResource` and leaves the critical region.

The purpose is to avoid deadlock if a lower filter reenters the top of the filter stack while this filter is holding the instance resource.

### `FmmEndFileSystemOperation`

Called after the filter-issued filesystem operation completes.

Behavior:

- Reacquires `MetadataResource` exclusive.
- Asserts the transition flag is still set.
- Clears `INSTANCE_CONTEXT_F_TRANSITION`.

Other threads that acquire the resource during the transition detect the flag and avoid reading or modifying the context.

## Optional `FmmIsMetadataOpen`

Compiled only when `VERIFY_METADATA_OPENED` is enabled.

Behavior:

- Gets the instance context.
- Acquires metadata resource shared.
- If not in transition, returns whether `INSTANCE_CONTEXT_F_METADATA_OPENED` is set.
- Asserts flag/pointer consistency:
  - Open flag implies handle and file object are non-null.
  - No open flag implies both are null.

## Error and Synchronization Model

The core concurrency model is:

- Normal metadata state changes require exclusive `MetadataResource`.
- Filter-issued filesystem operations drop that resource temporarily.
- The transition flag prevents other threads from acting on half-stable state.
- `STATUS_FILE_LOCK_CONFLICT` is used as the benign “try again or ignore because transition” signal.

## Research Notes

`DataStore.c` is the key file for understanding how the MetadataManager sample avoids self-deadlocks while maintaining a metadata file. The metadata contents are intentionally left as placeholders; the sample is about safe metadata-file ownership and release/reacquire choreography, not about a concrete metadata format.
