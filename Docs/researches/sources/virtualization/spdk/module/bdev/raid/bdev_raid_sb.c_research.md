# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid_sb.c

This file implements RAID superblock allocation, initialization, CRC validation, loading, writing, and clearing.

`raid_bdev_alloc_superblock()` allocates a DMA-zeroed buffer large enough for the maximum superblock length aligned to the bdev block size. `raid_bdev_free_superblock()` frees the main superblock plus any separate I/O buffer or metadata buffer used for interleaved/separate metadata formats.

`raid_bdev_init_superblock()` fills signature, version, UUID, RAID name, RAID size, data block size, RAID level, strip size, number of base bdevs, and base descriptors. Each configured base record stores UUID, data offset, data size, configured state, and slot number. `raid_bdev_sb_update_crc()` zeroes and recalculates CRC32C over the declared length; `raid_bdev_sb_check_crc()` recalculates without permanently changing the stored CRC.

Read-side parsing starts by reading enough blocks for the fixed superblock header. `raid_bdev_parse_superblock()` validates signature, declared length, CRC, supported major version, warns on newer minor version, and verifies base slot numbers. If the declared length exceeds the current read buffer but is within maximum bounds, it returns `-EAGAIN`; `raid_bdev_read_sb_remainder()` reallocates and reads the remaining bytes. For interleaved metadata bdevs, the read callback compacts data portions out of full block+metadata records before parsing.

`raid_bdev_load_base_bdev_superblock()` allocates a read context, opens a DMA buffer sized to the fixed header in device block units, submits `spdk_bdev_read()`, and returns the parsed superblock pointer only for the lifetime of the callback. Invalid signature/CRC/version are reported as `-EINVAL`, which callers use as "no valid RAID superblock" in examine paths.

Write-side I/O uses `raid_bdev_write_sb_ctx` to fan out writes to all configured, non-removing base bdevs. `raid_bdev_alloc_sb_io_buf()` prepares a write buffer: interleaved metadata gets a separate full-block buffer with data packed at each block start; non-interleaved writes use `raid_bdev->sb` directly and allocate a separate metadata buffer when the bdev has separate metadata. `raid_bdev_write_superblock()` increments the sequence number, updates the CRC, packs interleaved buffers if necessary, and submits `spdk_bdev_write_blocks_with_md()` to each base. `-ENOMEM` queues on the base bdev wait queue and resumes from the saved submitted index.

`raid_bdev_clear_superblock()` zeroes the prepared superblock I/O buffers and writes zeros to the superblock area on all configured bases. All write/clear calls assert they run on the SPDK app thread and call the supplied completion after every base slot is accounted for. The code treats skipped unconfigured/removing bases as successful fanout entries.
