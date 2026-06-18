# File Research: sources/virtualization/libguestfs/daemon/dropcaches.c

Implements Linux page/cache dropping.

Key points:
- Calls `sync_disks()` first.
- Writes the requested integer to `/proc/sys/vm/drop_caches`.
- Used by debug/bmap/qtrace paths to force cache effects before reads.
- Reports sync/open/write-close failures through daemon errors.
