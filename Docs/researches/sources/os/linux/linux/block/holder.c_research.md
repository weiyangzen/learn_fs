# File Research: sources/os/linux/linux/block/holder.c

Implements deprecated holder/slave sysfs link helpers between a claimed slave block device and a holding disk.

Key responsibilities:
- Tracks holder links in `struct bd_holder_disk`, keyed by the slave block device holder directory.
- Creates reciprocal sysfs links:
  - holder disk `slaves/<slave>`
  - slave bdev `holders/<holder>`
- Reference-counts duplicate links between the same slave and holder.
- Keeps an extra reference on `bd_holder_dir` so links can be cleaned up after disk deletion starts.

Important functions:
- `bd_link_disk_holder()` validates inputs, keeps holder directory lifetime, creates sysfs links, and records/refcounts the link.
- `bd_unlink_disk_holder()` decrements the refcount and removes links when it reaches zero.

Concurrency/lifetime notes:
- `blk_holder_mutex` serializes holder-list changes.
- The slave disk `open_mutex` is used to verify the slave disk is still live while acquiring the holder directory reference.
- Self-links are rejected.

Research relevance:
- This is a small compatibility bridge for block stacking visibility, used by existing holder users such as device-mapper style relationships.
