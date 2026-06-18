# File Research: sources/os/linux/linux-stable/fs/ext4/fast_commit.h

This header defines the ext4 fast commit on-disk TLV format, status codes, ineligibility reason IDs, in-memory tracking records, replay state, and tag-name helper.

Major contents:
- On-disk tags:
  - `EXT4_FC_TAG_ADD_RANGE`
  - `EXT4_FC_TAG_DEL_RANGE`
  - `EXT4_FC_TAG_CREAT`
  - `EXT4_FC_TAG_LINK`
  - `EXT4_FC_TAG_UNLINK`
  - `EXT4_FC_TAG_INODE`
  - `EXT4_FC_TAG_PAD`
  - `EXT4_FC_TAG_TAIL`
  - `EXT4_FC_TAG_HEAD`
- `EXT4_FC_SUPPORTED_FEATURES` is currently `0x0`.
- On-disk structures:
  - `struct ext4_fc_tl`: common tag and length header.
  - `struct ext4_fc_head`: feature bits and transaction ID.
  - `struct ext4_fc_add_range`: inode plus serialized extent bytes.
  - `struct ext4_fc_del_range`: inode, logical block, and length.
  - `struct ext4_fc_dentry_info`: parent inode, target inode, and flexible filename.
  - `struct ext4_fc_inode`: inode number plus flexible raw inode payload.
  - `struct ext4_fc_tail`: transaction ID and CRC.
- Kernel-only structures:
  - `struct ext4_fc_dentry_update`: queued in-memory dentry operation and name snapshot.
  - `struct ext4_fc_stats`: commit counters, block counters, average commit time, and ineligibility reason counters.
  - `struct ext4_fc_alloc_region`: physical block regions reserved during replay.
  - `struct ext4_fc_replay_state`: replay counters, CRC state, region array, and modified-inode array.

Important design points:
- The file comments state this header must remain byte-identical with the e2fsprogs copy.
- TLV structures are little-endian and intentionally compact for journal storage.
- `EXT4_FC_REPLAY_REALLOC_INCREMENT` grows replay arrays in small batches.
- `tag2str()` maps fast-commit tag values to trace/debug names.

Key invariants:
- On-disk format changes must be synchronized with userspace tooling.
- Flexible-array TLV payload lengths must be validated by replay before interpretation.
- `EXT4_FC_REASON_MAX` bounds both stats arrays and reason-name tables.
