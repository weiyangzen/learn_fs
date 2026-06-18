# File Research: sources/os/plan9/plan9/sys/src/9/port/devsegment.c

Purpose: Global shared-segment device `#g`. It lets users create named global segment directories, assign virtual address/length metadata, attach them through `segattach`, and read/write segment memory via a helper kernel process.

Key logic:
- Maintains up to 100 `Globalseg` objects with name, uid, permission, optional `Segment`, and a command rendezvous pair.
- `create` on the top directory creates a named segment directory.
- `ctl` accepts `va base length`, rounds to page boundaries, and creates an `SG_SHARED` segment with `newseg`.
- `data` reads/writes copy bytes through `segmentkproc`, whose address space maps the segment and executes `memmove` on requested offsets.
- `_globalsegattach` is installed so normal VM segment attach logic can find named global segments.

Dependencies and integration:
- Uses VM `Segment`, `newseg`, `putseg`, `isphysseg`, `isoverlap`, `segattach` hook, process segments, and Plan 9 device operations.

Risks and notes:
- Data I/O relies on a per-segment kproc to safely access the mapped virtual addresses.
- Segment deletion removes the global table entry and decrefs the object, but open refs keep it alive.
- Permissions are managed on `ctl`/`data`; directory perms are broadly listed as `0777`.
