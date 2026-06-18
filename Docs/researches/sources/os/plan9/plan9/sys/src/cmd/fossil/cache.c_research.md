# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/cache.c

Core block cache, allocator, write-order manager, and unlink/flush daemon layer for fossil.

The cache stores local disk blocks and Venti blocks in fixed memory slots, hashes them by address or score, tracks clean/dirty/read/write states, and keeps an LRU-like heap of unreferenced victims. Local scores are represented as mostly-zero Venti scores containing the disk address; global Venti scores are fetched through `vtRead`.

Allocation scans label blocks for free or reclaimable closed blocks, writes a new label, zero-extends data, and updates free-list accounting. Dirty blocks carry dependency lists so labels, newly copied blocks, parents, and superblock updates reach disk in safe order; if necessary, `blockRollback` writes an older safe image while keeping the current block dirty.

Copy-on-write and snapshot lifetime semantics are implemented through label epochs, `BsCopied`, `BsClosed`, and delayed unlink queues. Background threads flush dirty blocks, process block removals after durable parent writes, and periodically kick cache sync.
