# File Research: sources/os/linux/linux/fs/cramfs/inode.c

## Purpose
Implements the cramfs read-only filesystem: mount/fill-super paths, block or direct-MTD image reads, inode construction, directory lookup/readdir, file folio reads/decompression, optional direct physical mmap, statfs, and filesystem registration.

## Main Elements
- Superblock state: `struct cramfs_sb_info` stores magic, image size, block/file counts, feature flags, and optional linear virtual/physical MTD mapping.
- Inode numbering/building: `cramino()` derives stable inode numbers; `get_cramfs_inode()` initializes regular, directory, symlink, and special-file inodes from on-disk cramfs inodes.
- Image reads: blockdev mode uses a small private two-buffer cache in `cramfs_blkdev_read()`; MTD mode uses `cramfs_direct_read()` over a linearly mapped image; `cramfs_read()` selects the mode.
- Direct mapping support: `cramfs_get_block_range()`, `cramfs_last_page_is_shared()`, `cramfs_physmem_mmap()`, and NOMMU helpers map uncompressed direct-pointer ranges from MTD images when safe.
- Mount teardown/reconfigure: `cramfs_kill_sb()` unmaps MTD or releases block devices; `cramfs_reconfigure()` enforces readonly.
- Superblock validation: `cramfs_read_super()` reads the superblock at offset 0 or 512, checks magic/endian/features/root directory/root offset, and fills in format metadata.
- Fill-super variants: `cramfs_blkdev_fill_super()` initializes blockdev state; `cramfs_mtd_fill_super()` maps one page, validates size, remaps the full image, then finalizes root.
- Directory operations: `cramfs_readdir()` iterates padded directory entries; `cramfs_lookup()` scans entries, using sorted directory flag for early exits.
- Data read path: `cramfs_read_folio()` decodes block-pointer tables, handles direct/uncompressed/compressed/hole blocks, validates compressed block lengths, decompresses with zlib wrapper, and zero-fills page tails.
- Registration: `cramfs_fs_type` supports MTD first then blockdev fallback and uses `FS_REQUIRES_DEV`.

## Dependencies And Integration
Integrates VFS superblock/inode/dentry APIs, block-device page-cache reads, MTD direct mapping APIs, zlib decompression via `uncompress.c`, and cramfs on-disk structures from `uapi/linux/cramfs_fs.h`.

## Risk Notes
Cramfs trusts compact on-disk metadata after validation; malformed block pointers, zero namelens, bad compressed sizes, or unsupported flags produce errors. The global `read_mutex` serializes access to shared read buffers and single zlib stream. Direct mmap must reject writable VMAs, unaligned physical data, and shared last pages containing unrelated filesystem data.
