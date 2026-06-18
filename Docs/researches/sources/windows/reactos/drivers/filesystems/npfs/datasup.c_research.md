# File Research: sources/windows/reactos/drivers/filesystems/npfs/datasup.c

## Purpose
Implements NPFS data queue management. Each CCB owns inbound and outbound `NP_DATA_QUEUE` objects that hold queued reads, queued writes, buffered payloads, unbuffered IRPs, and special marker entries.

## Main Responsibilities
- `NpInitializeDataQueue` / `NpUninitializeDataQueue` set up and tear down queue state.
- `NpAddDataQueueEntry` inserts read or write entries:
  - Supports `Buffered`, `Unbuffered`, and internal special types `2` and `3`.
  - Captures client security context for write entries when needed.
  - Copies buffered write data into the queue entry allocation.
  - Marks pending IRPs and installs `NpCancelDataQueueIrp`.
- `NpRemoveDataQueueEntry` removes the head entry, updates byte/quota counters, releases security context, and handles cancellation races.
- `NpGetNextRealDataQueueEntry` skips special queue-marker entries and completes their IRPs.
- `NpCompleteStalledWrites` grants newly freed quota to previously queued buffered writes and completes write IRPs once their full quota is available.
- `NpCancelDataQueueIrp` removes a canceled IRP from its queue under the VCB lock, repairs counters, frees context, and completes cancellation.

## Queue Model
A queue is always in one of three states:
- `Empty`
- `ReadEntries`
- `WriteEntries`

The code asserts that new entries only join an empty queue or a queue already containing the same side of operation. This is the core invariant used by read/write/fsctl paths.

## Important Interactions
- Read path calls `NpAddDataQueueEntry(... ReadEntries ...)` when no data is available.
- Write path calls `NpAddDataQueueEntry(... WriteEntries ...)` when data cannot be fully delivered.
- `readsup.c` and `writesup.c` call `NpRemoveDataQueueEntry` and `NpCompleteStalledWrites`.
- `statesup.c` drains queues during disconnect/close transitions.
- Security context handoff is coordinated with `secursup.c`.

## Risks / Review Notes
- `NpAddDataQueueEntry` uses special numeric entry types `2` and `3` without named enum values, making flush/internal semantics harder to audit.
- The buffered-entry quota logic sets `HasSpace = TRUE` when quota is insufficient; the name is counterintuitive and should be read carefully.
- The cancel path must be kept consistent with all queue counter updates; it is central to avoiding stale pending IRPs and quota leaks.
