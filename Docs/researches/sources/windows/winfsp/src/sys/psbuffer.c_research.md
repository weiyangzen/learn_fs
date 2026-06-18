# File Research: sources/windows/winfsp/src/sys/psbuffer.c

## Purpose

`psbuffer.c` implements reusable per-process user-mode virtual buffers for WinFsp operations. It avoids repeated virtual memory allocation for small transfer buffers by caching a bounded number of buffers per process and cleaning them up when the process exits.

## Main Contents

- `FSP_PROCESS_BUFFER_ITEM` tracks one process ID, buffer count, and reusable buffer entries.
- `FSP_PROCESS_BUFFER_LIST_ENTRY` stores one virtual buffer pointer.
- A global spin lock protects a fixed hash table of process items.
- Functions:
  - `FspProcessBufferInitialize`
  - `FspProcessBufferFinalize`
  - `FspProcessBufferCollect`
  - `FspProcessBufferAcquire`
  - `FspProcessBufferRelease`
- `FspProcessBufferNotifyRoutine` hooks process creation/deletion notifications.

## Buffer Limits

- Maximum reusable buffer size is `FspProcessBufferSizeMax`, defined elsewhere as 64 KiB.
- Per-process reusable buffer count is:
  - 2 on systems with up to 2 processors,
  - up to 8 on larger systems,
  - otherwise equal to processor count.

## Control Flow

`FspProcessBufferAcquire`:

1. If requested size is within the reusable limit, looks up the current process ID.
2. Pops an available buffer entry if one exists.
3. If none exists and the process has capacity, allocates a new list entry and possibly a process item.
4. If capacity is exhausted, falls back to non-reusable direct virtual allocation.
5. Lazily allocates the actual virtual buffer to `FspProcessBufferSizeMax` with `ZwAllocateVirtualMemory`.
6. Returns a cookie when the buffer is reusable; returns a null cookie for direct allocations.

`FspProcessBufferRelease`:

- If a cookie exists, returns the buffer entry to the current process cache.
- If no cookie exists, releases the virtual memory directly.

`FspProcessBufferCollect`:

- Removes the process item from the hash table on process exit.
- Frees list-entry metadata.
- Does not free virtual memory in that path because the process address space is going away.

## Synchronization

- The process table and per-process buffer lists are protected by `ProcessBufferLock`.
- Allocation is intentionally done outside the spin lock when possible.
- If an entry cannot be returned because the process item disappeared, its virtual memory and metadata are freed.

## Integration

This is used by noncached read preparation paths when mapping/copying through a process-local buffer is preferable to exposing the original MDL mapping.

## Notable Details

- `SafeGetCurrentProcessId` uses `PsGetProcessId(PsGetCurrentProcess())`, avoiding deprecated direct current-process ID access.
- `Finalize` unregisters the process callback and frees remaining item/list metadata.
- Reusable virtual buffers are process-address-space allocations, so release must happen in the owning process context.
