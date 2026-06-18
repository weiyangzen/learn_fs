# File Research: sources/virtualization/spdk/lib/bdev/part.c

`part.c` provides common infrastructure for partition-like virtual bdevs backed by a base bdev. It handles base construction, base lifetime, partition construction/destruction, I/O channel creation, I/O remapping, hotremove, and DIF/DIX reference-tag remapping.

A `spdk_bdev_part_base` owns the opened base descriptor, base bdev pointer, refcount, module/fn_table pointers, tailq of partitions, custom channel callbacks, free callback, remove callback, and the thread where the base was opened. Closing the base descriptor is posted back to the opening thread when needed.

Partition destruction unregisters the io_device asynchronously, removes the partition from the base tailq, decrements the base refcount, releases the claimed base bdev when the last partition is gone, completes bdev destruction, and frees partition-owned strings and memory.

The partition I/O table blocks raw NVMe passthrough I/O types because a partition cannot safely decode and remap arbitrary NVMe commands. Other supported I/O types are delegated based on the base bdev’s support.

I/O submission remaps partition-relative offsets by adding `part->internal.offset_blocks`. It handles read, write, write zeroes, unmap, flush, reset, abort, zcopy, compare, compare-and-write, copy, and write-uncorrectable operations. Reads and writes use extended I/O options to preserve memory-domain and metadata pointers.

DIF reference-tag remapping is a key behavior. For writes, it remaps from partition-relative reference tags to base-device reference tags before submission. For reads, completion remaps tags back from base offsets to partition offsets. It supports interleaved metadata via `spdk_dif_remap_ref_tag()` and separate metadata via `spdk_dix_remap_ref_tag()`.

Base construction opens the named base bdev with an event callback, stores module/fn-table/tailq/free/channel callbacks, and records the thread. Partition construction copies base geometry and metadata/DIF properties, assigns name/product, generates a deterministic SHA1 UUID from base UUID plus offset/length unless an explicit UUID is supplied, claims the base bdev on first partition, registers an io_device, registers the child bdev, and inserts it into the base tailq.

Research notes: this is shared infrastructure for many virtual bdev modules. The most sensitive areas are base-claim lifetime, async destructor ordering, thread-affine close handling, and DIF remapping correctness.
