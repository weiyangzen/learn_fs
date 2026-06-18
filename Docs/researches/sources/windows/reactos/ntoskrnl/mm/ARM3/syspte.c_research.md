# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/syspte.c

ReactOS ARM3 system PTE allocator for reserving, releasing, coalescing, and initializing kernel system PTE pools.

Key responsibilities:
- Defines global system PTE state: `MmSystemPteBase`, per-pool start/end arrays, `MmFirstFreeSystemPte`, `MmTotalFreeSystemPtes`, `MmTotalSystemPtes`, `MiNumberOfExtraSystemPdes`, and size-bucket helper tables.
- Stores free system PTEs as singly linked clusters ordered by increasing cluster size.
- Encodes one-PTE clusters with `u.List.OneEntry`; multi-PTE clusters store the cluster size in the second PTE's `NextEntry`.
- Provides `MI_GET_CLUSTER_SIZE()` to decode cluster sizes.
- Provides `MiReserveAlignedSystemPtes()` and `MiReserveSystemPtes()` for allocation.
- Provides `MiReleaseSystemPtes()` for zeroing, coalescing adjacent free clusters, and reinserting them by size.
- Provides `MiInitializeSystemPtes()` for boot-time pool setup.

Important behavior:
- Reservation acquires `LockQueueSystemSpaceLock`, finds the first cluster large enough, unlinks it, and allocates from the tail of the cluster.
- If reservation splits a cluster, the remaining prefix is reinserted into the free list at the size-sorted position.
- Successful reservation decrements `MmTotalFreeSystemPtes[PoolType]`, releases the lock, and flushes the process TLB.
- Release zeroes the PTE range, acquires the same lock, increments the free count, scans the entire free list, merges adjacent clusters on either side, then creates one merged cluster and inserts it by size.
- Initialization creates a single free cluster spanning the given PTE range and records the total system PTE count for `SystemPteSpace`.

Dependencies:
- Uses ARM3 PTE structures and list encoding from `miarm.h`.
- Uses queued spin lock `LockQueueSystemSpaceLock`.
- Uses `MI_SYSTEM_PTE_BASE`, `MM_EMPTY_PTE_LIST`, `MMSYSTEM_PTE_POOL_TYPE`, `MMPTE`, and TLB flush helpers.

Notable risks:
- The `Alignment` parameter to `MiReserveAlignedSystemPtes()` is only asserted to be `<= PAGE_SIZE`; it is not otherwise used to select an aligned run.
- `MiInitializeSystemPtes()` asserts `NumberOfPtes >= 1` but writes the size into the second PTE, so practical callers must provide at least two PTEs.
- Allocation is linear over the free-cluster list and release scans the whole list, so fragmentation and large lists directly affect allocator cost.
- Release does not flush the TLB after zeroing PTEs, unlike reservation.
- Size-bucket globals such as `MmSysPteIndex`, `MmSysPteTables`, and `MmSysPteListBySizeCount` are present but not used by this implementation.
