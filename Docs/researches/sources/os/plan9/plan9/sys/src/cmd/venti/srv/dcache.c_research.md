# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dcache.c

Implements the raw disk block cache used for arena and metadata blocks. `getdblock()`/`_getdblock()` locate or load a `DBlock`, apply read or write locking based on mode, and read missing bytes from the underlying `Part` unless opened as pure write.

The cache uses a hash table for lookup, a free list, and an LRU-like heap based on second-to-last use to select victims. Dirty blocks are tagged with ordered dirty stages, and `flushproc()` writes all dirty blocks in stage order after sorting by dirty tag, partition, and address.

Writes are delegated to per-partition `writeproc()` workers through `Part.writechan`, then flushed per partition. `dirtydblock()` schedules immediate or delayed flush rounds when the dirty population grows.

The file also provides cache consistency checks, eviction through `emptydcache()`, and manual/forced flush or kick functions used by HTTP controls and index-write backpressure.
