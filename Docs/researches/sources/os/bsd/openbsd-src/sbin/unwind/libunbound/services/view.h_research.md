# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.h

`view.h` declares named view support for local-zone authority service. `struct views` contains an RW lock and rbtree of `struct view`; the documented lock order places the views lock before forwards, hints, anchors, and local-zone locks.

`struct view` is keyed in the tree by its `name` and holds view-specific `local_zones`, a view response-IP set, an `isfirst` flag controlling fallback to global local zones, and a per-view lock. The name field is deliberately placed immediately after the rbtree node because `view_create()` uses lock-protection pointer arithmetic over the non-node fields.

The API covers create/delete, applying config, comparing tree entries, deleting one view, debug printing, finding a named view with read/write lock acquisition, memory accounting for the tree or one view, and swapping the internal tree with preallocated data. The header exposes the locking expectations needed by config reload and query-time view lookup code.
