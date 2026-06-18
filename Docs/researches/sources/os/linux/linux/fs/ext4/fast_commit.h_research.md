# File Research: sources/os/linux/linux/fs/ext4/fast_commit.h

Defines the ext4 fast-commit on-disk TLV format and in-kernel replay/tracking structures.

Key behavior:
- Defines fast-commit TLV tags:
  - `ADD_RANGE`
  - `DEL_RANGE`
  - `CREAT`
  - `LINK`
  - `UNLINK`
  - `INODE`
  - `PAD`
  - `TAIL`
  - `HEAD`
- Defines on-disk value structures for head, add range, delete range, dentry info, inode snapshot, and tail CRC/tid.
- Defines fast-commit status codes used for stats.
- Defines all fast-commit ineligibility reason enum values.
- Under `__KERNEL__`, defines:
  - `struct ext4_fc_dentry_update`
  - `struct ext4_fc_stats`
  - `struct ext4_fc_alloc_region`
  - `struct ext4_fc_replay_state`
- Provides `tag2str()` for debug/trace-friendly tag names.
- Notes that this header must remain byte-identical with the e2fsprogs copy.

Important interactions:
- Shared contract between kernel fast-commit writer/replay code and userspace fsck/libext2fs understanding of fast-commit records.
- Replay state tracks valid tags, CRC progress, excluded allocation regions, and modified inode lists.
