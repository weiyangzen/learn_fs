# File Research: sources/os/linux/linux/fs/hfsplus/wrapper.c

Purpose: Handles low-level HFS+ volume wrapper discovery and volume-header I/O, including plain HFS+ volumes, HFSX volumes, HFS wrapper MDBs, partition-block discovery, and CD-ROM multisession offsets.

Key functions:
- `hfsplus_submit_bio()` performs aligned block-device I/O using `hfsplus_min_io_size()`, returning an offset data pointer for unaligned logical HFS+ sectors.
- `hfsplus_read_mdb()` parses an HFS wrapper MDB, validates embedded HFS+ signatures and wrapper flags, and extracts allocation-block and embedded-volume extents.
- `hfsplus_get_last_session()` resolves the selected or last CD-ROM data session using CD-ROM TOC/multisession APIs.
- `hfsplus_read_wrapper()` initializes minimum I/O size, reads primary and backup volume headers, follows wrappers/partition maps, validates signatures/block sizes, sets superblock block size, and records HFS+ partition offsets.

Dependencies and integration:
- Uses Linux block-device helpers, CD-ROM APIs, HFS partition discovery, and HFS+ raw constants.
- Populates `struct hfsplus_sb_info` fields such as `s_vhdr`, `s_backup_vhdr`, `alloc_blksz`, `blockoffset`, `part_start`, `sect_count`, and `fs_shift`.

Risk notes:
- Correctness depends on sector and block-size alignment; writes rely on buffers matching prior aligned reads.
- Wrapper/partition rediscovery uses `goto reread`, so corrupt metadata can steer repeated reads until validation fails.
- Memory allocated for volume-header buffers is freed only on error paths here; ownership transfers to mounted superblock state on success.
