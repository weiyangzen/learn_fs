# File Research: sources/os/linux/linux/block/blk-zoned.c

## Scope

This file implements zoned block device support: zone reporting and management ioctls, cached zone condition reporting, per-zone write plugs for sequential write ordering, zone append emulation, zone resource allocation/freeing, zone revalidation, and zoned zeroout fallback handling.

## Core State

- `struct blk_zone_wplug` tracks one sequential zone with hash/list nodes, plugged bio list, work item, RCU free head, disk pointer, spinlock, refcount, flags, zone number, write-pointer offset, and cached condition.
- Disk-level state used here includes `zones_cond`, `zone_wplugs_hash`, `zone_wplugs_pool`, `zone_wplugs_wq`, `zone_wplugs_worker`, active plug list, lock/completion fields, zone capacity fields, and `GD_ZONE_APPEND_USED`.
- Zone write plug flags:
  - `BLK_ZONE_WPLUG_PLUGGED` means writes are currently serialized through the plug.
  - `BLK_ZONE_WPLUG_NEED_WP_UPDATE` means a write error made the cached write pointer unreliable.
  - `BLK_ZONE_WPLUG_DEAD` means the plug is being removed after reset/finish/full-zone transitions.

## Public/Exported APIs

- Zone information:
  - `blk_zone_cond_str()` maps zone conditions to debug strings.
  - `bdev_zone_is_seq()` checks whether a sector is in a sequential-write zone.
  - `blkdev_report_zones()` calls the driver `report_zones` operation.
  - `disk_report_zone()` is a helper for drivers reporting zones and synchronizes plug write-pointer state.
  - `blkdev_get_zone_info()` and `blkdev_report_zones_cached()` synthesize reports from cached zone conditions and write plugs when valid.
- Zone management:
  - `blkdev_zone_mgmt()` validates and submits reset/open/close/finish/reset-all operations.
  - `blkdev_report_zones_ioctl()` handles `BLKREPORTZONE` and `BLKREPORTZONEV2`.
  - `blkdev_zone_mgmt_ioctl()` handles `BLKRESETZONE`, `BLKOPENZONE`, `BLKCLOSEZONE`, and `BLKFINISHZONE`.
  - `blk_zone_mgmt_bio_endio()` updates cached state after successful reset/reset-all/finish bios.
- Write plugging:
  - `blk_zone_plug_bio()` decides whether write, write zeroes, zone append, and zone management bios need plug handling.
  - `blk_zone_write_plug_bio_merged()`, `blk_zone_write_plug_init_request()`, `blk_zone_append_update_request_bio()`, `blk_zone_write_plug_bio_endio()`, and `blk_zone_write_plug_finish_request()` connect plugs to merge, request initialization, completion, and zone append sector reporting.
- Resource lifecycle:
  - `disk_init_zone_resources()`, `disk_free_zone_resources()`, and `blk_revalidate_disk_zones()` allocate, validate, resize, publish, and free zone condition/plug resources.
  - `blk_zone_issue_zeroout()` retries zeroout without no-fallback after refreshing the write pointer if hardware offload is unsupported.

## Control Flow Highlights

- Regular writes and write zeroes to sequential zones are serialized by `blk_zone_wplug_handle_write()`.
- Zone append is either passed to native hardware while marking `GD_ZONE_APPEND_USED`, or emulated by converting the bio to `REQ_OP_WRITE | REQ_NOMERGE` at the current plug write pointer and restoring the append op on completion.
- Plugged bios preserve order in `zwplug->bio_list`; per-zone work or the disk worker submits the next bio after completion depending on `QUEUE_FLAG_ZONED_QD1_WRITES`.
- Rotational mq zoned devices can use QD=1 write handling through the disk worker, while other devices use per-plug workqueue submission.
- On write failure, all queued bios for the plug are aborted and the plug is marked as needing a write-pointer update; report/reset/finish is required to recover reliable state.
- Revalidation reports all zones, checks zone gaps, type/condition consistency, power-of-two zone size, capacity, and constant sequential-zone capacity except for the last zone.

## Dependencies and Invariants

- Relies on driver `report_zones`, block bio/request helpers, RCU, mempools, kthreads, freezer support, blk-mq submission, and block tracepoints.
- Bios must not straddle zones when reaching write plug handling.
- Cached reports are not used after native zone append because native append can change conditions/write pointers outside plug tracking.
- Zone write plugs are refcounted and RCU-freed; the initial hash-table reference is dropped when the zone is reset, finished, or full.
