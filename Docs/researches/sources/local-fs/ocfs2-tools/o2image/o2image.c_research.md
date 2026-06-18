# File Research: sources/local-fs/ocfs2-tools/o2image/o2image.c

`o2image.c` implements the `o2image` utility for creating and installing OCFS2 metadata images. It scans OCFS2 metadata structures, marks blocks in an `ocfs2_image_state` bitmap, then writes either compact image format with an `ocfs2_image_hdr` plus bitmap trailer or raw sparse-positioned metadata blocks.

Core traversal starts at the global inode allocator, recursively visits inode allocators, chain allocators, extent trees, indexed directory dx roots, and indexed xattr buckets. Regular file data is intentionally skipped except metadata reachable through system allocators or xattr trees. Backup superblocks and pre-first-cluster-group blocks are always marked.

The writer supports regular seekable outputs with `pwrite64()` and non-seekable outputs by streaming zero-filled holes before metadata blocks. Install mode reverses argument meaning, opens compact images with `OCFS2_FLAG_IMAGE_FILE` unless raw is requested, and always writes raw format to the destination device/file.

Important dependencies are `libocfs2`, `ocfs2/image.h`, OCFS2 on-disk structures, image bitmap helpers, and system file lookup APIs. Risk areas include destructive install mode, interactive prompting based on estimated image size, incomplete recovery if traversal hits corrupt metadata, and cleanup paths assuming an initialized `ofs->ost`.
