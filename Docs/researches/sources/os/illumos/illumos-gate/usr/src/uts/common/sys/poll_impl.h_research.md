# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll_impl.h

## Purpose
Defines private caching-poll subsystem structures and routines used by `poll(2)`, `/dev/poll`, event ports, and recursive poll/epoll-style operations.

## Main Interfaces
- Core types:
  - `pollcache_t`
  - `pollstate_t`
  - `pcachelink_t`
  - `polldat_t`
  - `pollcacheset_t`
  - `xref_t`
- Cache sizing and hash constants:
  - `POLLFDSETS`
  - `POLLMAXDEPTH`
  - `POLLCHUNKSHIFT`
  - `POLLHASHCHUNKSZ`
  - `POLLHASHINC`
  - `POLLHASHTHRESHOLD`
  - `POLLHASH`
  - `POLLMAPCHUNK`
- Poll state flags/results:
  - `POLLSTATE_STALEMATE`
  - `POLLSTATE_ULFAIL`
  - `PSE_SUCCESS`
  - `PSE_FAIL_DEPTH`
  - `PSE_FAIL_LOOP`
  - `PSE_FAIL_DEADLOCK`
  - `PSE_FAIL_POLLSTATE`
- Cross-reference sentinels:
  - `POLLPOSINVAL`
  - `POLLPOSTRANS`
- Recursive cache link states:
  - `PCL_INIT`, `PCL_VALID`, `PCL_STALE`, `PCL_INVALID`, `PCL_FREE`
- Pollcache flags:
  - `PC_POLLWAKE`
  - `PC_EPOLL`
  - `PC_PORTFS`
- Internal routines:
  - `pollnotify()`
  - `pollhead_clean()`
  - `polldat_associate()`, `polldat_disassociate()`
  - `pollstate_create()`, `pollstate_destroy()`, `pollstate_enter()`, `pollstate_exit()`
  - `pcache_alloc()`, `pcache_create()`, `pcache_insert()`, `pcache_poll()`, `pcache_clean()`, `pcache_destroy()`
  - `pcache_lookup_fd()`, `pcache_alloc_fd()`, `pcache_insert_fd()`, `pcache_delete_fd()`, `pcache_grow_hashtbl()`, `pcache_grow_map()`, `pcache_update_xref()`, `pcache_clean_entry()`, `pcache_wake_parents()`
  - `pcacheset_create()`, `pcacheset_destroy()`, `pcacheset_cache_list()`, `pcacheset_remove_list()`, `pcacheset_resolve()`, `pcacheset_cmp()`, `pcacheset_invalidate()`, `pcacheset_reset_count()`, `pcacheset_replace()`

## Dependencies And Relationships
Includes `sys/poll.h`, `sys/thread.h`, `sys/file.h`, and `sys/port_kernel.h`. Event ports intentionally present a `port_fdcache_t` through `t_pollcache`, requiring matching lock/flag offsets with `pollcache_t`.

## Research Notes
The header documents the caching design in detail: per-thread `pollstate_t`, reusable `pollcache_t`, fd bitmaps, polldat hash tables, cached user pollfd sets, and parent/child cache links for recursive polling.
