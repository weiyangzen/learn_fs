# File Research: sources/windows/dokany/sys/directory.c

## Role

Implements directory control dispatch for directory enumeration and change notification.

## Main Functions

- `DokanDispatchDirectoryControl`
- `DokanQueryDirectory`
- `DokanNotifyChangeDirectory`
- `DokanCompleteDirectoryControl`

## Behavior

- Dispatches minor functions:
  - `IRP_MN_QUERY_DIRECTORY`
  - `IRP_MN_NOTIFY_CHANGE_DIRECTORY`
- `DokanQueryDirectory`:
  - Validates CCB/VCB.
  - Allocates an MDL for user buffer if needed.
  - Initializes or reuses per-CCB search pattern.
  - Tracks enumeration index in `ccb->Context`.
  - Builds `EVENT_CONTEXT` with directory name, search pattern, requested information class, buffer length, and index.
  - Registers the request as pending for user mode.
- `DokanNotifyChangeDirectory`:
  - Requires the FCB to be a directory and not delete-pending.
  - Marks debug flags.
  - Registers the IRP with `FsRtlNotifyFullChangeDirectory`.
  - Sets `DoNotComplete` because FsRtl owns/completes the IRP.
- `DokanCompleteDirectoryControl`:
  - Copies user-mode directory data back to the IRP buffer.
  - Updates enumeration index and user context.
  - Frees allocated MDL if this path allocated it.

## Dependencies

- `dokan.h`
- FsRtl directory notification APIs.
- MDL helpers from core Dokan functions.
- User-mode event completion contract through `EVENT_INFORMATION`.

## Notes and Risks

- Search pattern lifetime is per CCB and freed when CCB is freed.
- The code notes that writing `ccb->Context` may need locking.
- Directory notification stores a pointer to the FCB filename in FsRtl state, so FCB lifetime and notification cleanup are important.
