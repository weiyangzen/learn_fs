# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/expool.c

## Purpose

`expool.c` implements ReactOS ARM3 executive pool management: nonpaged and paged pool descriptors, small-block page subdivision, large-page pool allocation tracking, pool tag accounting, quota-aware allocation, debug validation, and public `Ex*Pool*` entry points.

## Main State

- Global pool descriptors and vectors:
  - `NonPagedPoolDescriptor`
  - `ExpPagedPoolDescriptor`
  - `PoolVector`
  - `ExpPagedPoolMutex`
- Pool tag tracking:
  - `PoolTrackTable`, `PoolTrackTableSize`, `PoolTrackTableMask`
  - `ExpTaggedPoolLock`
  - `PoolHitTag`, `ExStopBadTags`
- Large allocation tracking:
  - `PoolBigPageTable`, `PoolBigPageTableSize`, `PoolBigPageTableHash`
  - `ExpLargePoolTableLock`
  - `ExpPoolBigEntriesInUse`
  - `ExpBigTableExpansionFailed`
- Runtime/debug flags and counters:
  - `ExpPoolFlags`
  - `ExPoolFailures`
  - `MiLastPoolDumpTime`

## Pool Block Model

Small pool allocations are stored inside pages split into `POOL_BLOCK_SIZE` units. Each block has a `POOL_HEADER` with:

- `BlockSize`
- `PreviousSize`
- `PoolType`
- `PoolTag`

Free blocks reuse payload space as linked-list entries. Helper macros derive headers, free-list links, next blocks, and previous blocks from allocation addresses.

## Free-List Hardening

The file wraps pool free-list operations with encoded list pointers and consistency checks:

- `ExpEncodePoolLink` sets the low bit.
- `ExpDecodePoolLink` clears the low bit.
- `ExpCheckPoolLinks` verifies forward/backward symmetry and bugchecks on corruption.
- `ExpInitializePoolListHead`, `ExpIsPoolListEmpty`, `ExpRemovePoolEntryList`, `ExpRemovePoolHeadList`, `ExpRemovePoolTailList`, `ExpInsertPoolHeadList`, and `ExpInsertPoolTailList` implement encoded-list operations.

These checks are active rather than debug-only in this source snapshot.

## Pool Validation

- `ExpCheckPoolHeader` validates neighboring block sizes, page-boundary consistency, and nonzero block sizes.
- `ExpCheckPoolAllocation` validates an allocation tag, optionally validates pool type, and handles large page allocations through `PoolBigPageTable`.
- `ExpCheckPoolBlocks` walks all blocks on a pool page and verifies that a target block is present and the page layout is coherent.
- `ExpCheckPoolIrqlLevel` enforces pool IRQL rules:
  - paged pool at `APC_LEVEL` or lower
  - nonpaged pool at `DISPATCH_LEVEL` or lower

## Tag Accounting

- `ExpComputeHashForTag` hashes tags into the pool tracker table.
- `ExpSeedHotTags` preloads 64 common tags to reduce collisions.
- `ExpInsertPoolTracker` increments allocation counters and bytes for a tag.
- `ExpRemovePoolTracker` increments free counters and subtracts bytes for a tag.
- `ExGetPoolTagInfo` snapshots tag accounting with `KeGenericCallDpc` and returns `SYSTEM_POOLTAG_INFORMATION`.
- Debug builds expose `MiDumpPoolConsumers`, which prints tag usage and supports filtering by tag and wildcard mask.

ReactOS does not yet support tracker expansion for the normal tag table; overflow prints and ignores accounting for the tag.

## Large Pool Tracking

Allocations larger than `POOL_MAX_ALLOC` are page allocations backed by `MiAllocatePoolPages`.

- `ExpComputePartialHashForAddress` hashes allocation base addresses.
- `ExpAddTagForBigPages` inserts a large allocation into `PoolBigPageTable`.
- `ExpFindAndRemoveTagBigPages` removes a large allocation and returns its tag and page count.
- `ExpReallocateBigPageTable` grows or shrinks the large allocation tracker, rehashes live entries, swaps global table state under `ExpLargePoolTableLock`, frees the old table, and updates tag accounting for the tracker allocation itself.

The table grows near high utilization and shrinks at low utilization. If insertion fails after expansion, the allocation falls back to the synthetic `' GIB'` tag.

## Initialization

- `ExInitializePoolDescriptor` initializes descriptor counters, pending free fields, lock metadata, and all size-class list heads.
- `InitializePool` initializes either nonpaged or paged pool:
  - nonpaged pool setup allocates and zeros tag tables, seeds hot tags, allocates and initializes the large page table, initializes locks, and initializes `NonPagedPoolDescriptor`.
  - paged pool setup allocates a descriptor plus guarded mutex, initializes paged-pool vectors, and inserts tracker accounting for the nonpaged tag table allocation.

Session pool and NUMA pool variants are asserted unsupported.

## Allocation Path

`ExAllocatePoolWithTag` is the main allocator.

For large allocations:

- calls `MiAllocatePoolPages`
- handles must-succeed and raise-on-failure behavior
- updates descriptor counters
- records the allocation in the big pool table
- inserts tag accounting
- returns the page-aligned allocation

For small allocations:

- converts requested bytes plus header to a block count
- tries per-CPU and global lookaside lists for small block sizes
- searches descriptor free lists for a same-or-larger free block
- splits oversized free blocks while preserving `PreviousSize` links
- allocates a fresh page when no free block is available
- inserts leftover space into the appropriate free list
- updates descriptor and tag accounting
- returns the payload address after the header

Verifier and special pool hooks are present. Driver verifier is mostly a stub, while special pool is delegated to `MmAllocateSpecialPool` when enabled and applicable.

## Free Path

`ExFreePoolWithTag` handles both large and small allocations.

For large allocations:

- determines pool type by address
- removes the tag from the big pool table
- validates the optional caller-supplied tag
- removes tag accounting
- updates descriptor counters
- frees pages with `MiFreePoolPages`

For small allocations:

- reads the header, block size, pool type, and tag
- validates IRQL and optional tag
- removes tag accounting
- returns process quota if the allocation was quota-charged
- tries to push small blocks into lookaside lists
- otherwise merges adjacent free blocks on the same page
- frees the whole page if the merged block spans the page
- reinserts the merged block into the descriptor free list

`ExFreePool` is the tagless wrapper around `ExFreePoolWithTag`.

## Quota Support

- `ExAllocatePoolWithQuotaTag` adds `QUOTA_POOL_MASK`, reserves room for an owning `EPROCESS` pointer when possible, allocates pool, charges process quota, stores the owner at the end of the block, and references the process.
- `ExAllocatePoolWithQuota` uses `TAG_NONE`.
- `ExReturnPoolQuota` separately returns quota for a live allocation and clears the stored process pointer.
- Freeing quota-charged pool validates the stored process object type before returning quota and dereferencing it.

Quota is not charged for the initial system process and not used for large/page-aligned allocations where the owner pointer cannot be stored.

## Other Public APIs

- `ExAllocatePool` wraps `ExAllocatePoolWithTag` with `TAG_NONE`.
- `ExAllocatePoolWithTagPriority` currently ignores priority except for an `UNIMPLEMENTED` notice when allocation fails.
- `ExQueryPoolUsage` reports page and allocation/free totals for paged/nonpaged pools and lookaside hits.
- `ExQueryPoolBlockSize` is unimplemented.

## Notable Details

- Many malformed pool states lead to `KeBugCheckEx` with `BAD_POOL_HEADER`, `BAD_POOL_CALLER`, `MUST_SUCCEED_POOL_EMPTY`, or `NO_MORE_SYSTEM_PTES`-style failures depending on context.
- `ASSERT(!(PoolType & SESSION_POOL_MASK))` appears repeatedly; session pool is not implemented here.
- Large pool tracker resizing releases the spin lock before freeing the old table and updating tag accounting.
- `ExAllocatePoolWithTag` asserts `NumberOfBytes != 0`, but still has compatibility code to treat zero-byte requests as one byte after the assertion.
- The allocator uses several Windows-compatible behaviors: must-succeed pool bugchecks, raise-on-failure exceptions, optional failure debug prints, special pool hooks, and pool tag accounting.
