# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag.h

This header declares the refcount bag API.

Public operations:
- initialize/free an `rcbag`,
- add an rmap record,
- count stored items,
- find the next refcount edge,
- remove records ending at an edge,
- dump diagnostics.

The API is intentionally opaque: users see `struct rcbag` only as a handle. The implementation in `rcbag.c` uses the in-memory btree defined by `rcbag_btree.c`.
