# File Research: sources/os/linux/linux-stable/fs/ext4/bitmap.c

## Purpose

Provides ext4 bitmap free-bit counting and metadata checksum helpers for inode and block bitmaps.

## Main Responsibilities

- Counts free bits in a bitmap buffer.
- Verifies inode bitmap checksums.
- Sets inode bitmap checksums.
- Verifies block bitmap checksums.
- Sets block bitmap checksums.

## Key Operations

- `ext4_count_free()` returns total bits minus `memweight()`.
- `ext4_inode_bitmap_csum_verify()` checks `bg_inode_bitmap_csum_lo` and optional high checksum field when `metadata_csum` is enabled.
- `ext4_inode_bitmap_csum_set()` computes and stores inode bitmap checksum fields.
- `ext4_block_bitmap_csum_verify()` checks block bitmap checksum using cluster count.
- `ext4_block_bitmap_csum_set()` computes and stores block bitmap checksum fields.

## Dependencies

- Includes `<linux/buffer_head.h>` and `ext4.h`.
- Uses `ext4_chksum()`, superblock checksum seed, descriptor size, and metadata checksum feature detection.

## Research Notes

These helpers are called by allocation and inode-allocation code to detect metadata corruption. Checksumming is feature-gated; without `metadata_csum`, verification succeeds and setters return without changing descriptors.
