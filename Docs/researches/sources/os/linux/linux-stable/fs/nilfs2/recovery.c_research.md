# File Research: sources/os/linux/linux-stable/fs/nilfs2/recovery.c

`recovery.c` implements mount-time log validation, latest-super-root search, and roll-forward recovery of data-sync logs written after the latest checkpoint. It defines internal segment validation result codes and recovery work records for data blocks.

Checksum and validation flow is central. `nilfs_compute_checksum()` computes CRC32 across one or more contiguous blocks. `nilfs_read_super_root_block()` reads and optionally validates a super-root block checksum. `nilfs_validate_log()` checks segment summary magic, sequence number, block-count bounds, and full-log checksum. Validation failures are translated to warnings or errors by `nilfs_warn_segment_error()`.

Summary parsing helpers walk segment summary blocks across block boundaries. `nilfs_scan_dsync_log()` parses file info and virtual block info entries for data-sync logs, creating `nilfs_recovery_block` records with inode, physical block, virtual block, and file block offset. `nilfs_recover_dsync_blocks()` loads each inode from the recovered root, prepares a write_begin path, copies old log data into the page cache, marks files dirty, and counts salvaged blocks.

`nilfs_search_super_root()` starts from the superblock’s last partial segment, validates partial segments in sequence, follows `ss_next` across full segments, records used segments, and updates `the_nilfs` cursor fields (`ns_pseg_offset`, `ns_seg_seq`, `ns_segnum`, `ns_cno`, `ns_ctime`, `ns_nextnum`) when it finds a valid super root. If newer logs without a super root are found after the last checkpoint, it records roll-forward bounds in `nilfs_recovery_info`.

`nilfs_salvage_orphan_logs()` attaches the latest checkpoint, performs roll-forward if needed, prepares segment usage state for recovery, attaches a temporary log writer, constructs a recovery segment, detaches the writer, and post-cleans the roll-forward start block when appropriate. Failed roll-forward aborts by purging dirty recovery inodes from `ns_dirty_files`.

Segment preparation interacts heavily with `sufile`: it frees the obsolete next segment, scraps segments written after the latest super root so they are not immediately reused, allocates a fresh segment for recovery output, and advances sequence state. This file is the bridge between on-disk log scanning and normal segment construction.
