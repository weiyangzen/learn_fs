# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/disk.c

Asynchronous raw disk I/O layer over a fossil-formatted file or device.

`diskAlloc` reads and validates the fossil header, initializes queues and rendezvous objects, and starts `diskThread`. Raw reads/writes translate partition-relative block addresses through header partition offsets and use `pread`/`pwrite`; `diskFlush` waits for the queue to drain and uses a no-op `dirfwstat` as the Plan 9 flush mechanism.

Queued I/O is sorted into current/next scans by block address. The disk thread locks blocks, performs reads or writes, applies `blockRollback` for dependency-safe writes, updates block I/O state, and wakes flow/flush waiters.
