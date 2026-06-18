# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/image.h

## Purpose

Defines the packed/raw o2image file format header, runtime image state, bitmap mapping structures, and image helper API declarations.

## Main Contents

- Documents packed image format: image header, packed metadata blocks, and a bitmap mapping filesystem blocks to image blocks.
- Documents raw image format as sparse file with metadata blocks at filesystem offsets.
- Defines image magic, descriptor string, version, read modes, bitmap block size, and bits-per-bitmap-block.
- `struct ocfs2_image_hdr` stores image metadata including filesystem block count/size, image block count, bitmap block size, and backup superblock locations.
- `ocfs2_image_bitmap_arr` maps chunks of bitmap storage in memory and keeps cumulative set-bit counts.
- `struct ocfs2_image_state` stores runtime image metadata, inode allocator references, bitmap block accounting, backup superblocks, and loaded bitmap array.
- Declares bitmap load/free/alloc/mark/test, filesystem-to-image block translation, and header byte-swapping functions.

## Dependencies and Integration

- Depends on OCFS2 constants and `ocfs2_filesys`.
- Used by libocfs2 I/O wrappers so tools can operate on o2image files through normal block reads.

## Research Notes

- Packed image access depends on the in-memory bitmap for block translation, while raw image access can preserve block offsets.
