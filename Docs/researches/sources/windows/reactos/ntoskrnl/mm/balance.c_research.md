# File Research: sources/windows/reactos/ntoskrnl/mm/balance.c

## Role In Subset

Implements ReactOS memory balancing: per-consumer page accounting, page release/request helpers, consumer trimming, user-page aging/pageout, cache trimming integration, and the balancer system thread.

## Main Responsibilities

- Initializes `MiMemoryConsumers`, minimum available-page thresholds, and user consumer target in `MmInitializeBalancer`.
- Registers per-consumer trim callbacks with `MmInitializeMemoryConsumer`.
- Releases consumer pages with `MmReleasePageMemoryConsumer`, decrementing page usage and total committed pages before dereferencing PFNs.
- Trims a consumer with `MiTrimMemoryConsumer`, calculating targets from global pressure and per-consumer page targets.
- Implements `MmTrimUserMemory`, which either aggressively pages out LRU user pages or first clears accessed bits and later pages out cold pages.
- Triggers memory balancing through `MmRebalanceMemoryConsumers` and synchronous `MmRebalanceMemoryConsumersAndWait`.
- Allocates pages through `MmRequestPageMemoryConsumer`, updating consumer usage and total committed pages.
- Runs `MiBalancerThread`, which waits on an event or periodic timer, trims memory consumers, trims cache via `CcRosTrimCache`, and bugchecks if no progress is possible.
- Creates and prioritizes the balancer thread in `MiInitBalancerThread`.

## Important Behavior

- User trimming uses reverse-map entries to find process/address mappings for a physical page.
- To avoid PFN/address-space lock ordering problems, it repeatedly snapshots rmap entries under PFN lock, then references/attaches to processes and takes working-set locks before touching PTE accessed bits.
- The balancer timer fires every two seconds.
- `PageOutThreadActive` prevents concurrent event-triggered balancing runs.

## Notable Limitations

- `CanWait` in `MmRequestPageMemoryConsumer` is not meaningfully used; failure returns `STATUS_NO_MEMORY`.
- A static delay hack throttles every 100 page requests to give the memory manager recovery time.
- `MmTrimUserMemory` has a circular LRU detection abort path if it returns to the first page.
- Failure to trim when target remains unchanged causes `NO_PAGES_AVAILABLE` bugcheck.
- Some logic is tuned with fixed thresholds (`256` pages) and comments indicate suboptimal behavior.

## Filesystem-Relevant Notes

This file directly affects filesystem/cache pressure. It invokes cache trimming through `CcRosTrimCache`, pages out user pages, and manages page availability for memory consumers such as nonpaged pool and user memory, all of which influence filesystem buffering, mapped-file residency, and paging reliability.
