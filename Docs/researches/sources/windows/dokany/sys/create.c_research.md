# File Research: sources/windows/dokany/sys/create.c

## Role

Implements `IRP_MJ_CREATE`, the central Dokan open/create path. It normalizes names, manages FCB/CCB creation, handles related-file opens, validates write/share/oplock constraints, packages security metadata, and dispatches create requests to user mode.

## Main Functions

- CCB lifecycle:
  - `DokanAllocateCCB`
  - `DokanFreeCCB`
- Helpers:
  - `DokanGetParentDir`
  - `FixFileNameForReparseMountPoint`
  - `SetFileObjectForVCB`
  - `IsDokanProcessFiles`
  - `DokanCheckShareAccess`
  - `DokanRetryCreateAfterOplockBreak`
- Create path:
  - `DokanDispatchCreate`
  - `DokanCompleteCreate`

## Behavior

`DokanDispatchCreate` performs:

- Early rejection for missing file objects, unmounted volumes, unsupported paging files, and read-only write attempts.
- Reparse mount-point filename case repair on older Windows versions.
- Volume-open handling for empty filenames.
- Related-file-object path composition.
- Trailing and duplicated slash normalization.
- UNC prefix stripping.
- Alternate data stream rejection unless enabled.
- Parent-directory extraction for `SL_OPEN_TARGET_DIRECTORY`.
- FCB lookup/allocation and CCB allocation.
- File object binding:
  - `FsContext` to FCB advanced header.
  - `FsContext2` to CCB.
  - `SectionObjectPointer` to FCB section pointers.
- Security descriptor assignment and packaging into an event buffer.
- Share access checking through `IoCheckShareAccess`, `IoSetShareAccess`, and `IoUpdateShareAccess`.
- Oplock checks, break/retry handling, and atomic create-with-oplock support.
- Pending IRP registration for user mode.

`DokanCompleteCreate`:

- Copies user context into CCB.
- Sets IRP status and create information.
- Handles read-only `FILE_OPEN_IF` substitution result.
- Marks directory FCBs.
- Marks CCB as opened.
- Records delete-on-close for cleanup.
- Increments `UncleanCount` on success.
- Sends create notifications.
- On failure, backs out atomic oplock, removes share access, frees CCB/FCB, and clears file-object contexts.

## Dependencies

- `dokan.h`
- `util/fcb.h`
- `util/str.h`
- Windows I/O manager create parameters.
- Security APIs:
  - `SeAssignSecurity`
  - `SeDeassignSecurity`
- FsRtl oplock APIs.
- FCB AVL/cache management via `DokanGetFCB` and `DokanFreeFCB`.

## Important State

- `fcb->OpenCount`
- `fcb->UncleanCount`
- `fcb->ShareAccess`
- `ccb->UserContext`
- `ccb->AtomicOplockRequestPending`
- FCB flags:
  - directory
  - delete pending
  - block user-mode dispatch

## Notes and Risks

- This file is the highest-risk concurrency path in the group.
- Several paths require careful unwind of CCB/FCB/share/oplock state.
- The code comments document races around delete-pending and create completion.
- Filename manipulation supports multiple Windows edge cases: related opens, reparse mount points, UNC redirector paths, root alternate streams, and target-directory opens.
