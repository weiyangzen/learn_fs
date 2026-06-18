# File Research: sources/os/linux/linux/fs/nilfs2/recovery.c

`recovery.c` validates NILFS logs, finds the newest usable super root, and optionally rolls forward orphan data-sync logs written after the last checkpoint. It is the mount-time recovery companion to segment construction.

The file defines internal segment validation results and maps them to warnings or errors. `nilfs_compute_checksum()` calculates CRCs over contiguous log blocks. `nilfs_read_super_root_block()` reads and optionally verifies a super root checksum. `nilfs_validate_log()` checks segment summary magic, sequence number, block-count bounds, and full-log data checksum.

Summary parsing helpers walk segment summary blocks across block boundaries. `nilfs_scan_dsync_log()` extracts per-file data block records from data-sync logs into `struct nilfs_recovery_block` entries, recording inode number, disk block, virtual block, and file block offset.

`nilfs_search_super_root()` starts from the superblock’s last partial segment and follows segment summaries, validating each log, tracking sequence numbers, next segment numbers, latest checkpoint number, and possible newer orphan logical segments. It updates `the_nilfs` cursor fields such as `ns_pseg_offset`, `ns_seg_seq`, `ns_segnum`, `ns_cno`, `ns_ctime`, and `ns_nextnum`.

`nilfs_salvage_orphan_logs()` attaches the latest checkpoint, scans newer data-sync logs, copies recoverable data blocks back into files with `block_write_begin()`/`block_write_end()`, prepares fresh segments, constructs a recovery segment, and then zeroes the old roll-forward start block when needed. Failure paths abort roll-forward by purging dirty recovery inodes.
