# File Research: sources/windows/winfsp/src/sys/ioq.c

## Purpose

`ioq.c` implements WinFsp's core IRP queue abstraction, `FSP_IOQ`. It is the bridge between kernel IRP dispatch and the user-mode filesystem transaction loop: IRPs are posted as pending work, moved to processing while user mode handles them, and optionally placed on a retried-completion queue when completion must be retried later.

## Main Contents

- A long design comment documents the pending/processing flow and why an event-backed queue is used instead of a semaphore or manual-reset event.
- `FSP_IOQ_USE_QEVENT` selects WinFsp queued events; the fallback synchronization-event path is deliberately disabled with a compile-time `#error`.
- Optional `FSP_IOQ_PROCESS_NO_CANCEL` provides custom cancel-safe queue helpers that avoid setting a cancellation routine after an IRP enters processing.
- `FSP_IOQ_PEEK_CONTEXT` carries either an IRP boundary/hint or an expiration timestamp for queue scans.
- Three cancel-safe queues are implemented over one `FSP_IOQ` spin lock:
  - `PendingIoCsq`: newly posted IRPs waiting for user-mode pickup.
  - `ProcessIoCsq`: IRPs currently in user-mode processing, also indexed by a hash table for hint lookup.
  - `RetriedIoCsq`: IRPs whose completion needs retry.
- Each queue has callback functions for insert, remove, peek, lock acquire/release, and canceled-IRP completion.
- Public lifecycle and query functions:
  - `FspIoqCreate`
  - `FspIoqDelete`
  - `FspIoqStop`
  - `FspIoqStopped`
  - `FspIoqRemoveExpired`
  - `FspIoqPostIrpEx`
  - `FspIoqNextPendingIrp`
  - `FspIoqPendingIrpCount`
  - `FspIoqPendingAboveWatermark`
  - `FspIoqStartProcessingIrp`
  - `FspIoqEndProcessingIrp`
  - `FspIoqProcessIrpCount`
  - `FspIoqRetryCompleteIrp`
  - `FspIoqNextCompleteIrp`
  - `FspIoqRetriedIrpCount`

## Control Flow

A normal IRP flow is:

1. Dispatch code calls `FspIoqPostIrpEx`.
2. The IRP receives a timestamp unless posted as best effort.
3. It is inserted into the pending cancel-safe queue.
4. User-mode transact code calls `FspIoqNextPendingIrp`, which waits on `PendingIrpEvent` if a timeout was supplied, then removes a pending IRP.
5. The IRP enters processing via `FspIoqStartProcessingIrp`, where it is inserted into `ProcessIoCsq`.
6. Later, completion finds/removes it with `FspIoqEndProcessingIrp`.
7. If completion must be deferred, `FspIoqRetryCompleteIrp` inserts it into the retried queue and wakes transact waiters.
8. `FspIoqNextCompleteIrp` drains retried completions.

## Synchronization

- All queue state is protected by `Ioq->SpinLock`.
- Pending-queue availability is represented by `PendingIrpEvent`.
- `FspIoqPendingResetSynch` resynchronizes the event state with actual pending count or stop state.
- Processing IRPs are also stored in hash buckets keyed by mixed IRP pointer to support direct lookup by hint.

## Integration

This file is used by the WinFsp I/O processor and filesystem volume device extension to move IRPs between kernel dispatch and user-mode `FSP_FSCTL_TRANSACT` handling. The caller supplies `CompleteCanceledIrp`, so this queue layer does not decide how canceled IRPs are completed.

## Notable Details

- `FspIoqStop` marks the queue stopped, wakes waiters permanently, and optionally drains pending, processing, and retried queues through the cancellation callback.
- Expiration uses interrupt time converted to whole seconds, with timeout rounded up at queue creation.
- Best-effort IRPs are assigned `FspIrpTimestampInfinity` and are not expired by timestamp scans.
- `FspIoqPendingAboveWatermark` assumes `PendingIrpCapacity` is nonzero.

## Risks and Edge Cases

- In `FspIoqRemoveExpired`, the retried queue removal references `Ioq->RetryIoCsq`, while the rest of the file and `driver.h` use `RetriedIoCsq`. If this code path is compiled, that looks like a stale-name defect.
- Event correctness depends on every remove or failed dequeue resynchronizing pending state under the queue lock.
- The optional no-cancel processing mode changes cancellation semantics after an operation has been started, which is intentional but important for behavioral compatibility.
