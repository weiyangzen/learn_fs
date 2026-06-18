# File Research: sources/os/linux/linux-stable/fs/netfs/internal.h

Shared internal declarations and inline helpers for netfs and FS-Cache implementation files.

Key contents:
- Includes netfs, FS-Cache, folio queue, seq_file, slab, and trace headers.
- Declares request/subrequest allocation, read collection, write collection, retry, rolling buffer, proc, stats, and FS-Cache functions.
- Provides proc add/remove helpers for active netfs I/O requests.
- Defines stats increment/decrement helpers that compile away when disabled.
- Provides cache/cookie/volume state accessors with acquire/release ordering.
- Provides netfs group refcount helpers for dirty folio grouping.
- Provides request/subrequest in-progress checks with memory barriers.
- Defines debug macros and assertion macros used across these files.

Architectural role:
- This is the glue header connecting buffered read/write, FS-Cache, request lifetime, stats, and tracing.
