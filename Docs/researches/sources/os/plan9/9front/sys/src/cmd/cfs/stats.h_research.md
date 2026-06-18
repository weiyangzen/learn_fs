# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/stats.h

Statistics structures for optional `cfs` monitoring.

Key definitions:
- `Cfsmsg` stores call count and nanosecond accumulator/start timestamp for one 9P message type.
- `Cfsstat` stores client/server per-message arrays and aggregate counters: directory reads, delegated reads, inserts, deletes, updates, bytes read/written, bytes from server/dirs/cache, and bytes written to cache.

Dependencies:
- Used by `cfs.c` and inode update paths.

Research notes:
- Stats are exposed through the synthetic `cfsctl` file when `-S` is enabled.
