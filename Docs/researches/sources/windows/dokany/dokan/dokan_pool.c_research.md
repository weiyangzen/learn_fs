# File Research: sources/windows/dokany/dokan/dokan_pool.c

Global object-pool implementation for Dokan runtime buffers, open-info objects, directory vectors, and the shared Windows thread pool.

Key responsibilities:
- Creates the global thread pool with `CreateThreadpool`.
- Initializes critical sections for all pools.
- Allocates vector-backed pools for IO batches, IO events, default event results, 16K/32K/64K/128K event results, open info, and directory lists.
- Cleans up pooled objects, vectors, critical sections, and the thread pool.
- Provides pop/push/free functions for:
  - `DOKAN_IO_BATCH`
  - `DOKAN_IO_EVENT`
  - `EVENT_INFORMATION` result buffers
  - extra-sized event result buffers
  - `DOKAN_OPEN_INFO`
  - directory-list vectors
- Initializes per-open critical sections on first allocation and cleans cached directory lists/search patterns when returning open info to the pool.
- Uses `EventContextBatchCount` as a shared reference count for batched event contexts.

Important behavior:
- Pools are bounded; if a pool is full on push, the object is freed.
- Pop functions zero or reset metadata before returning objects.
- Extra event-result pools zero only the fixed header, leaving variable buffer memory uncleared unless the caller requested direct allocation clearing.
- `PushIoBatchBuffer()` decrements `EventContextBatchCount` and only returns/frees the batch once the count reaches zero.
- `PopDirectoryList()` returns a vector sized for `WIN32_FIND_DATAW` and clears its item count.

Dependencies:
- Uses `DOKAN_VECTOR` as the backing storage for pointer pools.
- Uses Windows critical sections and threadpool APIs.
- Depends on size macros from `dokan_pool.h` and protocol constants from Dokan headers.

Notable risks:
- `InitializePool()` does not unwind partially initialized resources if a vector allocation fails.
- Cleanup assumes all global pool vectors are non-null.
- `PopIoBatchBuffer()` allocates `DOKAN_IO_BATCH_SIZE`, while `FreeIoBatchBuffer()` simply frees; callers that allocate non-pool large batches must set `PoolAllocated` correctly.
- Open-info reuse depends on `CleanupFileOpenInfo()` clearing directory cache and search pattern every time.
