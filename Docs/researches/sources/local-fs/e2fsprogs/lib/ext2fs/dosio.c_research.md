# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.c

Implements a legacy DOS BIOS-backed libext2fs I/O manager. It exposes `dos_io_manager`, whose methods open DOS-accessible Linux-style device names, read and write sectors through BIOS INT 13h style calls, and close channels.

Core components:
- Global error state: `_dio_error`, `_dio_hw_error`.
- Cached partition table: `partitions`, `npart`, `active`.
- I/O manager methods: `dos_open`, `dos_close`, `dos_set_blksize`, `dos_read_blk`, `dos_write_blk`, `dos_flush`.
- Address conversion: `lba2chs`.
- Partition scanning: `scan_partition_table`.
- Channel allocation: `alloc_io_channel`.

Open behavior:
- Accepts paths under `/dev`, with `hd`, `sd`, or `fd` style names.
- Maps hard disk letters to BIOS physical drives starting at `0x80`.
- Does not support floppy access despite parsing `fd`.
- Reads drive geometry, reads MBR sector, scans for Linux ext2 partition type `0x83`, and rejects Linux swap type `0x82`.
- Caches partition metadata and returns a libext2fs `io_channel`.

Read/write behavior:
- Converts block number and channel block size into byte offset, then CHS.
- Uses `biosdisk` read/write commands.
- Negative `count` means byte count rather than block count, matching libext2fs IO convention.
- `dos_flush` is a no-op because there is no buffering.

Implementation notes:
- The source mutates the `dev` string temporarily despite receiving `const char *`, which is unsafe if passed immutable storage.
- `realloc(partitions, sizeof(PARTITION) * npart)` appears to size by struct rather than pointer and does not allocate room for the new entry when `npart` is current count.
- Extended partitions are explicitly unsupported for partition numbers >= 5, despite the header comment claiming extended traversal.
- The file is platform-specific and depends on DOS headers such as `<bios.h>` and `<io.h>`.
