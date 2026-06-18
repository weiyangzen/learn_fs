# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/swaplist.c

Implements swap listing for `swapctl`.

Behavior:
- Uses `swapctl(SWAP_NSWAP)` to count configured swap devices.
- Allocates `struct swapent` array and fills it with `swapctl(SWAP_STATS)`.
- Supports optional priority filtering.
- Supports long listing with device, size, used, available, capacity, and priority.
- Supports short summary with total allocated/used/available.
- Uses `getbsize()` unless `-k` forces 1K blocks.
- Converts disk blocks through `dbtob()`.

Filesystem/storage relevance:
- Read-only swap accounting/reporting layer over OpenBSD kernel swap state.
