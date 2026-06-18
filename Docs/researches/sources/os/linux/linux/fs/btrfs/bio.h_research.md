# File Research: sources/os/linux/linux/fs/btrfs/bio.h

## Scope And Role

`bio.h` defines Btrfs' high-level wrapper around the Linux block layer `struct bio`. The central type is `struct btrfs_bio`, which embeds a `struct bio` as its final member and adds filesystem context needed by Btrfs I/O submission, checksum verification/generation, read repair, mirror selection, split I/O completion tracking, and metadata parent checks.

This is an interface/header file only. It declares allocation, initialization, submission, completion, repair, and bioset lifecycle functions implemented elsewhere.

## Main Types And Constants

`BTRFS_BIO_INLINE_CSUM_SIZE` is `64`, used for small inline checksum storage in read bios.

`btrfs_bio_end_io_t` is the completion callback type:
`void (*)(struct btrfs_bio *bbio)`.

`struct btrfs_bio` contains:

- `inode` and `file_offset`: identify the Btrfs inode and logical file offset for the I/O. Data inodes get automatic checksum verification and read repair; metadata inodes are caller-managed.
- A union of operation-specific state:
  - Data reads store checksum pointer, inline checksum buffer, and saved iterator.
  - Data writes store ordered extent, checksum sums, checksum work/completion state, saved iterator, original physical address for zone append, and original logical address for fscrypt checksum handling.
  - Metadata reads store `struct btrfs_tree_parent_check`.
- `end_io_work`: work item for internal read end-I/O handling.
- `end_io` and `private`: caller-supplied completion callback and opaque context.
- `pending_ios`: tracks split/submitted child bios.
- `mirror_num`: selected mirror.
- `status`: first error status among split bios.
- Bit flags for commit-root checksum lookup, scrub bios, remapped-copy bios, async checksum generation, and zone append use.
- Embedded `struct bio bio`, deliberately last because `bio_alloc_bioset()` allocation sizing depends on it.

## Public API

`btrfs_bio(struct bio *bio)` converts a Linux `bio` pointer back to its containing `struct btrfs_bio`.

Bioset lifecycle:
- `btrfs_bioset_init()`
- `btrfs_bioset_exit()`

Bio lifecycle:
- `btrfs_bio_init()`
- `btrfs_bio_alloc()`
- `btrfs_bio_end_io()`

Submission and repair:
- `btrfs_submit_bbio()`
- `btrfs_submit_repair_write()`
- `btrfs_repair_io_failure()`

`REQ_BTRFS_CGROUP_PUNT` aliases `REQ_FS_PRIVATE` to request submission through `blkcg_punt_bio_submit`.

## Integration Points

This header depends on Linux block APIs (`linux/bio.h`), workqueues, and Btrfs tree checking (`tree-checker.h`). It is the shared contract between Btrfs read/write paths, checksum code, scrub/repair paths, and the lower-level physical-device mapping submission machinery.

The inode comment is important: data inodes trigger automatic data integrity behavior, while metadata callers retain responsibility for validation. That split is core to how Btrfs differentiates file data I/O from btree block I/O.

## Concurrency And State Notes

`pending_ios` and `status` support split I/O completion aggregation. The design records the first failing status and delays final completion until all child bios finish.

`end_io_work`, `csum_work`, and `csum_done` show that data I/O completion and checksum generation can be asynchronous.

The struct layout invariant, with `bio` last, is a hard ABI-style implementation constraint inside the filesystem's bioset allocation logic.

## Risks And Edge Cases

The union members are context-sensitive. Misusing a `btrfs_bio` as the wrong operation type would alias unrelated fields.

Zone append and fscrypt need original physical/logical addresses preserved, so write paths must populate `orig_physical` and `orig_logical` correctly.

`is_scrub` is needed because scrub can reuse the btree inode; callers must set it to prevent metadata/data behavior confusion.

## Testing Signals

Relevant tests should exercise:
- Data read checksum verification and read repair.
- Split bio completion error aggregation.
- Async write checksum generation.
- Scrub bios using btree inode context.
- Zone append write completion.
- Remapped copy I/O paths.
