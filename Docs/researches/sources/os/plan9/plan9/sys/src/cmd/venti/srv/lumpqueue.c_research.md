# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lumpqueue.c

Purpose: Implements asynchronous queued writes for Venti lumps.

Key behavior:
- `initlumpqueues` creates one queue worker per index section.
- `queuewrite` maps a lump score to an index section, appends a `WLump` to that section’s small ring buffer, and wakes its worker.
- `flushqueue` advances a generation counter and waits for queued entries from older generations to drain.
- `queueproc` removes queued writes, calls `writeqlump`, reports failures, and releases the lump reference.

Dependencies:
- Uses `indexsect`, `writeqlump`, `putlump`, `Rendez`, `QLock`, and global `mainindex`.

Notable details:
- Ring size is only 8 entries per queue.
- Writes are sharded by index section, preserving locality and reducing lock contention.
