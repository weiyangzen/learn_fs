# File Research: sources/os/linux/linux/block/genhd.c

Implements gendisk registration, device lifetime, major/minor allocation, disk/partition sysfs and proc exports, disk sequence numbers, and disk teardown.

Key responsibilities:
- Maintains block major registrations and optional legacy autoload probes.
- Allocates extended minors with an IDA.
- Registers disks as block-class devices, sets sysfs attributes, creates `holders`/`slaves` directories, registers queues and backing devices, and scans partitions.
- Removes disks, marks them dead, drops partitions, drains queues, unregisters queues/BDI, and releases resources.
- Exposes `/proc/partitions`, `/proc/diskstats`, and sysfs attributes such as `size`, `stat`, `inflight`, `diskseq`, `partscan`, `badblocks`, and read-only state.
- Allocates and releases `struct gendisk` and its `part0` block device.

Important functions:
- `set_capacity()` and `set_capacity_and_notify()` update disk capacity and send resize uevents.
- `__register_blkdev()` / `unregister_blkdev()` manage block major names.
- `disk_scan_partitions()` triggers partition rescans with exclusive-claim coordination.
- `add_disk_fwnode()` / `device_add_disk()` register disks.
- `del_gendisk()` and `__del_gendisk()` remove disks and coordinate queue draining.
- `__alloc_disk_node()` and `__blk_alloc_disk()` allocate gendisks and queues.
- `put_disk()` drops the final disk reference.
- `set_disk_ro()` changes disk read-only state and emits uevents.

Concurrency/lifetime notes:
- Disk add/remove around blk-mq uses `tag_set->update_nr_hwq_lock` and `memalloc_noio`.
- Deletion disables elevator switching before queue teardown.
- Disk death sets `GD_DEAD`, may set `QUEUE_FLAG_DYING`, sets capacity to zero, starts queue drain, and notifies block devices.
- `diskseq` is monotonic and helps userspace distinguish reused block names.

Research relevance:
- This file is the central Linux block-device object model and lifecycle implementation.
