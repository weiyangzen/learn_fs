# File Research: sources/windows/reactos/drivers/filesystems/npfs/npfs.h

## Purpose
Central NPFS private header. Defines node types, queue structures, VCB/DCB/FCB/CCB layouts, alias structures, locking helpers, deferred completion helper, and all internal function prototypes.

## Main Structures
- `NP_VCB`:
  - Global volume/device state.
  - Holds root DCB, prefix table, VCB resource lock, event table, and wait queue.
- `NP_DCB`:
  - Directory control block, currently root-focused.
  - Holds notify lists and child FCB list.
- `NP_FCB`:
  - Named pipe file control block.
  - Holds instance counts, pipe configuration/type, default timeout, CCB list, and security descriptor.
- `NP_CCB`:
  - Per pipe instance.
  - Holds state, read/completion mode per end, file objects per end, process/session metadata, nonpaged CCB, inbound/outbound queues, client security context, and listen IRP list.
- `NP_NONPAGED_CCB`:
  - Per-instance nonpaged lock and event-buffer pointers.
- `NP_DATA_QUEUE` / `NP_DATA_QUEUE_ENTRY`:
  - Queue state and queued read/write/data entries.
- `NP_WAIT_QUEUE` / `NP_WAIT_QUEUE_ENTRY`:
  - Global wait-for-pipe support with spinlock, timer, DPC, and IRP linkage.
- Alias structures:
  - `NPFS_ALIAS`
  - `NPFS_QUERY_VALUE_CONTEXT`

## Helper Patterns
- `NpAcquireSharedVcb`, `NpAcquireExclusiveVcb`, `NpReleaseVcb` wrap the global VCB `ERESOURCE`.
- `NpCompleteDeferredIrps` completes IRPs collected while locks were held, after the caller releases the VCB lock but remains inside the filesystem critical region.
- `NpBugCheck` embeds per-file source IDs into `NPFS_FILE_SYSTEM` bugchecks.

## Important Interactions
This header ties together the complete NPFS module set: create/open, state transitions, queue operations, wait support, security, read/write, fsctl, file/volume information, and structure allocation.

## Risks / Review Notes
- Queue entry types only name `Buffered` and `Unbuffered`, but implementation uses additional numeric values.
- The event table is declared in the VCB, but backing callbacks are stubbed in `strucsup.c`.
- `PNP_ROOT_DCB_FCB` appears as a typedef name for `NP_ROOT_DCB_CCB`, which is confusing but used consistently.
