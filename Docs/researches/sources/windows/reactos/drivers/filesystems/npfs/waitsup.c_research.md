# File Research: sources/windows/reactos/drivers/filesystems/npfs/waitsup.c

## Purpose
Implements `FSCTL_PIPE_WAIT` waiter queue support using a wait list, cancel routines, timers, DPCs, and name matching.

## Main Responsibilities
- `NpInitializeWaitQueue` initializes list and spinlock.
- `NpAddWaiter`:
  - Allocates a wait entry.
  - Initializes timer/DPC.
  - Upcases the requested pipe name in the caller buffer.
  - Stores wait queue and wait entry in IRP driver context.
  - Installs cancel routine and queues the IRP.
  - References the file object and sets a timer.
- `NpCancelWaitQueueIrp`:
  - Removes a canceled waiter under spinlock.
  - Cancels timer if possible.
  - Dereferences file object and frees wait entry.
  - Completes the IRP with `STATUS_CANCELLED`.
- `NpTimerDispatch`:
  - Removes timed-out waiter.
  - Clears cancel routine.
  - Completes with `STATUS_IO_TIMEOUT`.
- `NpCancelWaiter`:
  - Upcases the target pipe path.
  - Scans waiters for matching names.
  - Removes matching waiters, cancels timers, and queues their IRPs on a deferred completion list with caller-supplied status.
- `NpEqualUnicodeString` compares strings without calling routines unsafe under a spinlock.

## Important Interactions
- `fsctrl.c` queues waiters in `NpWaitForNamedPipe`.
- `create.c` and `strucsup.c` cancel waiters when pipe instances appear or disappear.
- Waiter completion follows the NPFS deferred-completion pattern.

## Risks / Review Notes
- Alias-name handling in `NpCancelWaiter` contains `ASSERT(FALSE)`, and alias translation is commented out in `NpWaitForNamedPipe`; alias waits are incomplete.
- Pool tag in `NpAddWaiter` uses `NPFS_WRITE_BLOCK_TAG` instead of `NPFS_WAIT_BLOCK_TAG`.
- Timer/cancel races are carefully handled through `WaitEntry->Irp = NULL` and IRP driver context clearing.
