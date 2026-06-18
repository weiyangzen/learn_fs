# sources/test-tools/fio/t/zbd/functions

## Purpose
`t/zbd/functions` is a shared Bash library for fio zoned block device tests. It abstracts discovery, geometry parsing, zone operations, capacity accounting, and fio log parsing across Linux `blkzone`, libzbc tools, SCSI inquiry data, NVMe ZNS devices, null_blk, block devices, and SG character devices.

## Important APIs, Types, and Functions
Command variables (`blkzone`, `sg_inq`, `zbc_report_zones`, `zbc_reset_zone`, `zbc_close_zone`, `zbc_info`) are initialized at load time and validated. Capability helpers include `has_command`, `is_nvme_zns`, `is_nullb_with_zone_cap`, `check_blkzone`, and `blkzone_reports_capacity`. Geometry helpers include `first_sequential_zone`, `first_online_zone`, `last_online_zone`, `total_zone_capacity`, `zone_cap_bs`, `max_open_zones`, `max_active_zones`, `min_seq_write_size`, `urswrz`, `zbc_physical_block_size`, and `zbc_disk_sectors`.

Device mutation helpers are `reset_zone()` and `close_zone()`, selecting `blkzone` or libzbc operations. Log helpers `fio_io()`, `fio_read()`, `fio_written()`, and `fio_reset_count()` parse human-readable fio output.

## Control Flow and State
The file is sourced by test scripts and immediately validates tool availability. Many functions depend on globals set by callers, especially `use_libzbc`, `is_zbd`, and `zone_size`. Most outputs are shell-printed values consumed by command substitutions.

## Dependencies and Integration Points
It integrates with `/sys/block`, `/sys/kernel/config/nullb`, SCSI VPD pages via `sg_inq`, `blkzone report/reset/close`, and libzbc report/reset/close/info tools. It is central to `test-zbd-support` and the null_blk/scsi_debug wrappers.

## Risks and Test Signals
Risks include fragile parsing of external command output, mixed hex/decimal handling, assumptions about 512-byte sectors, and global variable dependence. Strong signals are early command availability failures, geometry sanity failures, parsed fio byte counts, and reset-count extraction.
