# File Research: sources/windows/dokany/sys/cleanup.c

## Role

Handles `IRP_MJ_CLEANUP`, including share-access removal, file-lock cleanup, delete-on-close transfer, directory notification cleanup, keepalive-triggered unmounting, and optional user-mode cleanup dispatch.

## Main Functions

- `DokanExecuteCleanup`
- `DokanDispatchCleanup`
- `DokanCompleteCleanup`

## Behavior

- `DokanExecuteCleanup`:
  - Validates file object, VCB/DCB, and CCB.
  - Checks the CCB belongs to the current mount.
  - Decrements `fcb->UncleanCount`.
  - Removes share access.
  - Checks oplocks.
  - Unlocks all outstanding file locks for the file object/process.
- `DokanDispatchCleanup`:
  - Transfers `DOKAN_DELETE_ON_CLOSE` from CCB to FCB delete-pending state.
  - Reports file/directory removal notifications when the last unclean handle is closing.
  - Calls `FsRtlNotifyCleanup` for directories.
  - Handles keepalive file cleanup by triggering unmount.
  - If unmount is pending or user-mode dispatch is blocked, executes cleanup locally.
  - Otherwise flushes FCB state, builds an `EVENT_CONTEXT`, and registers a pending IRP for user mode.
- `DokanCompleteCleanup`:
  - Runs `DokanExecuteCleanup`.
  - Sets final IRP status from user-mode `EVENT_INFORMATION`.

## Dependencies

- `dokan.h`
- FCB/CCB flags and locks.
- FsRtl file locks and change notifications.
- User-mode event pipeline through `AllocateEventContext` and `DokanRegisterPendingIrp`.

## Notes and Risks

- Delete-on-close is deliberately delayed until cleanup and only acted on when the last handle closes.
- Comments call out a race where create may succeed while delete-pending state is being established.
- Keepalive cleanup can force unmount if the owning process exits.
