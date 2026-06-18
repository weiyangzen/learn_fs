# File Research: sources/local-fs/ocfs2-tools/libocfs2/openfs.c

Opens OCFS2 filesystems, reads/writes superblocks, and abstracts metadata reads for image files.

Block read abstraction:
- `__ocfs2_read_blocks()` handles normal devices and `OCFS2_FLAG_IMAGE_FILE`.
- For image files, it verifies every requested metadata block exists in the image bitmap and maps real block numbers to image-relative block numbers.
- Public wrappers are `ocfs2_read_blocks()` and `ocfs2_read_blocks_nocache()`.

Superblock handling:
- `ocfs2_validate_ocfs1_header()` rejects old OCFS1 volumes unless the caller requested no revision check.
- `ocfs2_read_super()` reads a candidate superblock, checks `OCFS2_SUPER_BLOCK_SIGNATURE`, creates a temporary swapped superblock so metadata ECC can be validated with the correct block size/super context, then returns/stores a CPU-endian superblock.
- `ocfs2_write_primary_super()` writes the primary superblock through inode write semantics.
- `ocfs2_write_super()` writes primary then refreshes backups.
- `ocfs2_write_backup_super()` copies the primary superblock, changes `i_blkno`, sets backup-super compat feature, and writes to the requested backup block.

Open flow:
- `ocfs2_open()` allocates `ocfs2_filesys`, opens the IO channel, stores the device name, optionally loads an o2image bitmap, detects hard read-only devices, rejects OCFS1 if appropriate, discovers or uses supplied block size and superblock block, reads the superblock, and validates feature compatibility.
- If no block size is supplied, it probes from IO block size up to `OCFS2_MAX_BLOCKSIZE`.
- Strict compat checks also validate tunefs-in-progress flags.
- Rejects unsupported incompat features, rejects unsupported ro-compat features when opening RW, and can reject heartbeat devices unless explicitly allowed.
- Validates blocksize bits, inode block number matching the chosen superblock, cluster-size range, root/system directory block numbers, and slot count.
- Allocates cached inode allocator arrays and extent-block allocator arrays sized by `s_max_slots`.
- Initializes cluster/block counts, root/sysdir block numbers, first cluster group, and printable UUID.

Utility helpers:
- `ocfs2_mount_local()` tests local-mount incompat feature.
- `ocfs2_is_hard_readonly()` exposes hard read-only device status.

Important invariants:
- `fs->fs_super` is CPU-endian after open.
- `fs->fs_blocksize` must match the superblock `s_blocksize_bits`.
- Opening read-write is refused when unsupported ro-compat features are present.
