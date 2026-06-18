# File Research: sources/local-fs/xfsdump/restore/win.c

## Summary
Implements an mmap window cache over a large file. It maps fixed-size file segments on demand, reference-counts them, and reuses idle windows through an LRU list.

## Main Responsibilities
- Initialize windowing over a backing fd, first file offset, segment size, and maximum window count.
- Map a segment index to a memory pointer, reusing existing mappings when possible.
- Unmap caller references and move idle windows onto an LRU list.
- Grow the segment-index-to-window map as new segment indexes are requested.
- Allow locking to be disabled during single-threaded tree reconstruction phases.
- Report how many mmap calls were made.

## Important Behavior
`win_init()` validates page alignment, allocates transient state, initializes the segment map, and allocates a qlock.

`win_map()` checks the segment map first. If the segment is already mapped, it removes an idle window from the LRU list if needed and increments the reference count. Otherwise it allocates a new window descriptor until `t_winmax`, or reuses the LRU head by `munmap()`ing the old segment.

`win_map()` calls `mmap_autogrow()` for the target segment and returns `NULL` if no window is available or mapping fails.

`win_unmap()` validates the pointer belongs to the mapped segment, decrements the reference count, adds newly idle windows to the LRU tail, and clears the caller’s pointer.

`win_locks_off()` and `win_locks_on()` bypass the qlock for phases known to be single-threaded.

## Dependencies
Depends on `qlock`, xfsdump logging/types, page-size globals, and `mmap_autogrow()`.

## Risks
There is one global `tranp`; the abstraction is not designed for multiple independent window caches in one process.

If all windows are referenced, mapping another segment fails and callers must handle a `NULL` pointer.

Mapping failure decrements `t_winmax`, which can permanently reduce mapping capacity for the process.

Correctness relies on every caller balancing `win_map()` with `win_unmap()`; leaked references prevent LRU reuse.
