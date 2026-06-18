# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/irp.c

## Role

`irp.c` implements core Windows-compatible IRP lifecycle services: allocation and lookaside reuse, construction helpers for FSD and IOCTL requests, synchronous forwarding, cancellation, thread IRP list management, completion unwinding, APC-based final completion, associated IRPs, reserve IRP handling, and requestor identity helpers. It is one of the central I/O-manager files because nearly every filesystem or storage path eventually relies on `IofCallDriver()` and `IofCompleteRequest()`.

## Main entry points and behavior

- `IoAllocateIrp()` allocates an IRP either from per-processor small/large lookaside lists or nonpaged pool, sets quota/fixed-size/lookaside allocation flags, initializes the packet with `IoInitializeIrp()`, and records allocation metadata for `IoFreeIrp()` (lines 610-709).
- `IoFreeIrp()` validates that the packet is detached from the thread IRP list and has advanced past the stack, then returns it to pool or the correct lookaside list, including quota return and lookaside-float accounting (lines 1661-1741).
- `IopInitializeReserveIrp()`, `IopAllocateReserveIrp()`, and `IopFreeReserveIrp()` provide a single preallocated reserve IRP with stack size 20, serialized through an interlocked in-use flag and event (lines 547-606). Completion of reserve synchronous paging IRPs returns the packet to the reserve allocator instead of freeing it (lines 1488-1502).
- `IoBuildAsynchronousFsdRequest()` creates read/write/flush/shutdown/PnP/power style IRPs and prepares buffered, direct, or neither I/O according to target device flags. It sets read/write byte offsets and stores caller `IO_STATUS_BLOCK` and thread (lines 745-874).
- `IoBuildSynchronousFsdRequest()` wraps the asynchronous builder, adds the caller event, and queues the IRP on the requestor thread cleanup/cancel list (lines 1064-1094).
- `IoBuildDeviceIoControlRequest()` builds external or internal device-control IRPs, handling `METHOD_BUFFERED`, direct methods, and `METHOD_NEITHER`, with MDL probing for direct output buffers and cleanup on probe failure (lines 876-1062).
- `IofCallDriver()` advances the IRP stack, stores the target device in the next stack location, and dispatches to the driver major-function table. It bugchecks on stack exhaustion (lines 1253-1288).
- `IofCompleteRequest()` is the completion engine. It detects double completion, walks stack locations upward, invokes completion routines according to success/error/cancel flags, propagates pending state, handles associated IRPs and master completion, preserves mount-point reparse buffers, releases auxiliary buffers, handles paging/close completion, unlocks MDL pages, supports deferred completion, and queues a kernel APC to run `IopCompleteRequest()` in the requestor thread (lines 1303-1607).
- `IopCompleteRequest()` is the final APC routine. It copies buffered input data back to user buffers, frees system buffers and MDLs, writes the user IOSB, signals user/file-object events, updates transfer counters, unqueues the IRP from the thread list, posts user APCs or completion-port packets, and releases file-object references (lines 236-545).
- `IoCancelIrp()` sets `Irp->Cancel`, atomically removes the cancel routine under the cancel spin lock, and calls it with `CancelIrql` if present; invalid completed-state cancellation bugchecks (lines 1096-1139).
- `IoCancelThreadIo()` cancels all IRPs on the current thread's list, waits for completion, and after a retry budget disassociates a broken-driver IRP through `IopDisassociateThreadIrp()` (lines 1141-1210).
- `IopDisassociateThreadIrp()` removes a stuck IRP from the current thread, clears its owner, logs an `IO_DRIVER_CANCEL_TIMEOUT` against the current stack's device if possible, and leaves the IRP detached (lines 113-187).
- `IoForwardIrpSynchronously()` copies the current stack to the next stack, installs a completion routine that signals an event, calls the next device, and waits if the result is pending (lines 1609-1659).
- `IoMakeAssociatedIrp()` allocates a child IRP, marks `IRP_ASSOCIATED_IRP`, copies the owner thread, and points back to the master IRP (lines 1920-1947).
- Requestor helpers include `IoGetRequestorProcess()`, `IoGetRequestorProcessId()`, `IoGetRequestorSessionId()`, `IoGetTopLevelIrp()`, `IoSetTopLevelIrp()`, and paging priority selection (lines 1743-1847, 1995-2004).

## Data, ownership, and synchronization

- The file uses per-processor lookaside lists through `KeGetCurrentPrcb()->PPLookasideList[]` and tracks quota interactions with `LookasideIrpFloat`.
- Thread-associated synchronous IRPs are protected by raising to APC level and by queued spin locks for I/O completion and cancellation paths.
- Completion is split between high-level stack unwinding in `IofCompleteRequest()` and passive-thread finalization in `IopCompleteRequest()` using `KAPC`.
- `IopDeadIrp` is a global diagnostic pointer for the latest disassociated stuck IRP.
- MDLs may be freed in builder error paths, associated-IRP completion, final APC cleanup, or explicit cleanup; locked pages are unlocked in `IofCompleteRequest()` before final APC queuing.

## Filesystem and storage relevance

This file defines the mechanics used by filesystem drivers to forward requests, split paging I/O, complete direct/buffered I/O, process reparse mount points, and wait for synchronous device and filesystem control operations. Any filesystem research in this tree depends on these completion and cancellation semantics.

## Implementation gaps and risks

- Asynchronous non-synchronous paging write completion is explicitly unimplemented and breaks into the debugger under the compiled path (lines 1505-1524).
- `IoIsValidNameGraftingBuffer()` is unimplemented and always returns `FALSE`, so name-grafting validation is absent (lines 1908-1918).
- `IoIs32bitProcess()` is unimplemented on `_WIN64` (lines 2006-2015).
- `IopAllocateIrpMustSucceed()` retries for a very large finite count after 10 ms sleeps, which approximates must-succeed behavior but is not a true guaranteed allocator (lines 711-743).
- `IoCancelThreadIo()` ignores its `Thread` parameter and always operates on the current thread, matching the local comment but surprising for callers expecting the signature semantics (lines 1146-1157).
