# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/utility.h

## Purpose

Provides small kernel-mode utility helpers for the `change` minifilter sample, mainly fast-mutex allocation and safe list iteration.

## API Surface

- Defines `CG_MUTEX_TAG`.
- `CgAllocateMutex()` allocates a zeroed `FAST_MUTEX` from `NonPagedPoolNx`.
- `CgFreeMutex()` frees a mutex with `CG_MUTEX_TAG`.
- `LIST_FOR_EACH_SAFE(curr, n, head)` iterates a doubly linked list while allowing removal of the current element.

## Dependencies And Usage

- `context.c` uses the mutex helpers for transaction context mutex allocation and cleanup.
- `change.c` uses `LIST_FOR_EACH_SAFE()` while draining transaction file-context lists.

## Risks And Invariants

- Fast mutex storage must remain in nonpaged pool; the helper encodes that requirement.
- `CgFreeMutex()` assumes the input pointer is valid and was allocated with `CG_MUTEX_TAG`.
- The safe-list macro assumes a standard initialized `LIST_ENTRY` head and valid `Flink` pointers.
