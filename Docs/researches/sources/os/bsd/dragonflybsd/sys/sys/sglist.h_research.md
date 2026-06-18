# File Research: sources/os/bsd/dragonflybsd/sys/sys/sglist.h

This kernel-only header defines scatter/gather list structures and APIs for physical address ranges.

Key responsibilities:
- Rejects userland inclusion.
- Defines `struct sglist_seg` with physical address and length.
- Defines `struct sglist`:
  - segment array
  - reference count
  - current segment count
  - maximum segment count
- Declares forward references for `mbuf` and `uio`.
- Defines inline helpers:
  - `sglist_init()`
  - `sglist_reset()`
  - `sglist_hold()`
- Declares allocation, append, build, clone, count, join, slice, split, length, free, and UIO consumption APIs.

Important invariants:
- `sglist_init()` initializes refcount to 1 and sets `sg_nseg` to 0.
- `sglist_reset()` clears only the used segment count, retaining storage and max segment capacity.
- `sglist_hold()` increments the reference count and returns the same pointer.

Research notes:
- This API is used for physical scatter/gather descriptions across kernel buffer, mbuf, UIO, and user memory paths.
