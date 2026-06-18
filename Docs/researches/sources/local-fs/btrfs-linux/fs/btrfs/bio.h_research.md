# File Research: sources/local-fs/btrfs-linux/fs/btrfs/bio.h

Public Btrfs bio wrapper interface.

Key points:
- Defines `BTRFS_BIO_INLINE_CSUM_SIZE` for inline checksum storage.
- Defines `btrfs_bio_end_io_t` callback type.
- `struct btrfs_bio` embeds a kernel `struct bio` as the final member and stores Btrfs-specific context before it.
- Common fields:
  - Target inode and file offset.
  - Completion callback and private data.
  - Pending split-I/O count.
  - Mirror number.
  - First saved error status.
  - Flags for commit-root checksum search, scrub, remap, async checksum, and zone append.
- Union payload covers:
  - Data reads: checksum buffer, inline checksum buffer, saved iterator.
  - Data writes: ordered extent, ordered sums, checksum work/completion, saved checksum iterator, original physical/logical addresses.
  - Metadata reads: parent-check structure.
- `btrfs_bio()` converts embedded `bio *` back to `struct btrfs_bio *`.
- Declares bioset init/exit, init/allocation, end I/O, submit, repair write, and read-repair failure APIs.
- Defines `REQ_BTRFS_CGROUP_PUNT` as `REQ_FS_PRIVATE`, used to submit through `blkcg_punt_bio_submit`.

Role in system:
- Establishes the high-level I/O container used by `bio.c` and callers throughout Btrfs.
- The layout requirement that `bio` is last is essential because `bio_alloc_bioset()` allocates enough memory for the whole wrapper.
