# File Research: sources/os/linux/linux-stable/fs/btrfs/bio.h

## Purpose

`bio.h` defines Btrfs' high-level I/O wrapper around the kernel `struct bio`. `struct btrfs_bio` carries filesystem-specific context needed before and after the generic block layer sees an I/O: inode/file offset, checksum state, ordered extent state, metadata parent checks, mirror selection, split-I/O accounting, and Btrfs end-I/O callbacks.

## Main Data Structures And APIs

- `BTRFS_BIO_INLINE_CSUM_SIZE` reserves 64 inline bytes for read checksum storage before falling back to external checksum memory.
- `btrfs_bio_end_io_t` is the Btrfs-level completion callback type.
- `struct btrfs_bio` embeds `struct bio` last, which is required because `bio_alloc_bioset()` allocates enough trailing memory based on that layout.
- `btrfs_bio()` converts a generic `struct bio *` back to `struct btrfs_bio *`.
- Bioset lifecycle:
  - `btrfs_bioset_init()`
  - `btrfs_bioset_exit()`
- Allocation and initialization:
  - `btrfs_bio_init()`
  - `btrfs_bio_alloc()`
- Completion/submission:
  - `btrfs_bio_end_io()`
  - `btrfs_submit_bbio()`
  - `btrfs_submit_repair_write()`
  - `btrfs_repair_io_failure()`
- `REQ_BTRFS_CGROUP_PUNT` aliases `REQ_FS_PRIVATE` for submission through `blkcg_punt_bio_submit`.

## State Carried By `struct btrfs_bio`

- Common fields:
  - `inode` and `file_offset` identify the data or metadata object covered by the I/O.
  - `end_io` and `private` carry caller completion context.
  - `pending_ios` tracks split physical I/Os under one logical Btrfs bio.
  - `mirror_num` selects or records a mirror.
  - `status` preserves the first split bio error.
- Data read union state:
  - `csum`, `csum_inline`, and `saved_iter` support checksum verification and read repair.
  - `csum_search_commit_root` forces checksum lookup against the commit root.
- Data write union state:
  - `ordered` links the bio to ordered extent completion.
  - `sums` points at checksums generated for writeback.
  - `csum_work`, `csum_done`, and `csum_saved_iter` support synchronous or async checksum calculation.
  - `orig_physical` is needed for zone append.
  - `orig_logical` is needed when checksumming fscrypt bios.
- Metadata read union state:
  - `parent_check` carries tree parentness verification state.
- Internal end-I/O state:
  - `end_io_work` allows read completion work to be deferred.
- Boolean flags distinguish scrub bios, remapped copy I/O, async checksums, and zone append eligibility.

## Integration Points

This header is shared by the Btrfs I/O stack. Data reads use it for checksum validation and read repair. Data writes use it to connect bios to ordered extents and checksum generation. Metadata callers use it for parent checks but remain responsible for metadata-specific validation. The repair APIs connect failed logical/file offsets to mirrors and physical addresses.

## Risks And Invariants

- `struct bio bio` must remain the last member; moving it would break bioset allocation assumptions.
- The union fields are context-specific. Callers must not interpret read checksum fields as write ordered-extent fields, or metadata parent-check fields as data-I/O fields.
- Split I/O completion depends on `pending_ios` and `status` preserving the first error while all split physical bios finish.
- Zone append and fscrypt checksum paths depend on `orig_physical` and `orig_logical` being populated consistently before submission.
