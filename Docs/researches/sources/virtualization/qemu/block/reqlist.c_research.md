# File Research: sources/virtualization/qemu/block/reqlist.c

Implements a small coroutine request-overlap list helper. `reqlist_init_req()` initializes a `BlockReq` with offset/byte range, creates its wait queue, and inserts it into a `BlockReqList`.

`reqlist_find_conflict()` scans the list for the first request whose byte range overlaps a requested range using `ranges_overlap()`. `reqlist_wait_one()` waits on the conflicting request's queue while holding a provided `CoMutex`; `reqlist_wait_all()` repeats until no overlapping request remains.

`reqlist_shrink_req()` reduces an active request's byte range and wakes all waiters so conflicts can be re-evaluated. `reqlist_remove_req()` removes the request and wakes all waiters. The helper is intended for block filters that need simple in-flight range exclusion.
