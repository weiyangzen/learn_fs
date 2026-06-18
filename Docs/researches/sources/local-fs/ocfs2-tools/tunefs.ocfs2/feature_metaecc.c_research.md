# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_metaecc.c

## Purpose
Enables or disables metadata ECC support.

## Main Behavior
- Enable:
  - Scans all inodes and metadata into an rb-tree of `block_to_ecc` records.
  - Stores write callbacks per block type: dinode, extent block, group descriptor, directory block.
  - Defers chain allocator scanning until after directory trailer installation because trailer work may allocate.
  - For directories without trailers, prepares trailer contexts and estimates extra blocks/clusters needed.
  - Verifies sufficient free clusters.
  - Sets `OCFS2_TUNEFS_INPROG_DIR_TRAILER` while installing trailers.
  - Installs directory trailers using `tunefs_install_dir_trailer()`.
  - Clears the in-progress bit.
  - Scans chain allocator group descriptors.
  - Sets `OCFS2_FEATURE_INCOMPAT_META_ECC` in memory.
  - Rewrites collected metadata blocks so checksums/ECC match the new feature state.
  - Writes the superblock.
- Disable:
  - Clears `OCFS2_FEATURE_INCOMPAT_META_ECC` and writes the superblock.
  - Does not remove directory trailers or rewrite all metadata.

## Dependencies
- OCFS2 rb-tree and kernel-list helpers.
- `tunefs_prepare_dir_trailer()` and `tunefs_install_dir_trailer()`.
- OCFS2 inode, extent, chain, group descriptor, directory block APIs.
- Tunefs in-progress flag helpers.

## Notes
The enable path is one of the most complex migrations in this group. It deliberately caches metadata before writing and uses an in-progress bit for directory trailer installation so fsck can reason about interruption.
