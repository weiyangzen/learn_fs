# File Research: sources/virtualization/spdk/module/bdev/raid/concat.c

This file implements the concatenated RAID level. It exposes multiple base bdev data regions as one logical bdev by laying each base range after the previous one, without striping or redundancy.

`concat_start()` allocates a `concat_block_range` array in `raid_bdev->module_private`. For each base slot it rounds data size down to a multiple of strip size, records the logical start and length, updates total block count, and stores the rounded size back into the base info. The resulting RAID block count is the sum of all rounded base sizes. The RAID bdev advertises `optimal_io_boundary = strip_size` and `split_on_optimal_io_boundary = true`, so normal read/write requests should not cross module-imposed boundaries.

`concat_submit_rw_request()` finds the base range containing `raid_io->offset_blocks`, computes the physical base LBA relative to that range, and submits a single `raid_bdev_readv_blocks_ext()` or `raid_bdev_writev_blocks_ext()` with memory domain and metadata options propagated. `-ENOMEM` queues the original RAID I/O for later resubmission on the selected base bdev; other submission errors complete the RAID I/O failed.

Flush and unmap can span multiple concatenated base ranges. `concat_submit_null_payload_request()` identifies the first and last affected base indices, initializes the expected child count, and submits range-specific flush/unmap operations across the involved bases. It tracks already submitted base I/Os for `-ENOMEM` resumption and uses `raid_bdev_io_complete_part()` to complete once all involved bases finish.

`concat_stop()` frees the range table synchronously. The registered module requires at least one base bdev, supports memory domains, and supplies start/stop/read-write/null-payload hooks. It has no redundancy and no resize hook in this file.
