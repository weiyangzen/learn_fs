# File Research: sources/local-fs/jfsutils/fscklog/extract.c

Implements extraction of the on-device fsck service log from a JFS aggregate into a displayable file.

Key contents:
- Uses `libfs` helpers for devices, disk maps, superblocks, endian conversion, utility math, and messages.
- Maintains global superblock buffer `aggr_superblock`, device stream `Dev_IOPort`, output stream `outfp`, raw fsck log buffer, and extracted log buffer.
- Entry point `xchklog()` initializes superblock pointer, performs initial processing, extracts records, and closes files/devices.
- `xchklog_initial_processing()` opens the target device read-only, validates a JFS superblock, computes fsck workspace and service-log offsets from `s_fsckpxd` and `s_fsckloglen`, selects new vs old half of the service-log area based on `s_fscklog`, and opens the output file.
- `extract_service_log()` reads raw fsck log buffers, walks `fscklog_entry_hdr` entries, endian-swaps headers on big-endian hosts, validates entry lengths, and records message text into the extracted output format.
- `xchklog_fscklog_fill_buffer()` reads from device offset, advances aggregate/log offsets, and stops after one half of the reserved fsck log area.
- `open_device_read()` opens a path with `fopen(..., "r")` and sets physical block/sector sizes to `PBSIZE`.
- `open_outfile()` chooses `fscklog.new` or `fscklog.old`, opens for write, writes the extracted-log eyecatcher into the output buffer, and reports output filename.
- `readwrite_device()` enforces sector alignment and delegates to `ujfs_rw_diskblocks()`.
- `record_msg()` wraps a message string in `chklog_entry_hdr`, aligns record length to 4 bytes, flushes full buffers, and tracks the last header to pad records over buffer boundaries.
- `validate_super()` checks magic/version, device size, physical/fs block sizes, flags, group commit, AG size, fsck workspace placement/length, and inline journal placement.
- `validate_superblock()` reads primary, falls back to secondary, validates, records aggregate block size, and reports which superblock is usable.

Interactions:
- Consumes on-disk structures from `jfs_superblock.h`, `jfs_filsys.h`, `jfs_types.h`, and `jfs_dmap.h`.
- Uses `libfs/devices.c` for device size and raw reads.
- Shares record state with `fscklog.c` and `display.c` through `struct fscklog_record`.

Research notes:
- Contains duplicated low-level routines also present in fsck code, explicitly noted as future libfs consolidation candidates.
- `record_msg()` uses `strcpy()` into a fixed 4096-byte stack buffer, assuming source fsck log messages are bounded.
