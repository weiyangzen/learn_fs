# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_file.h

## Purpose

Declares the XFS regular file and directory file operation tables and a fallocate alignment helper.

## Main Contents

- `xfs_file_operations`
- `xfs_dir_file_operations`
- `xfs_is_falloc_aligned`

## Research Notes

This header is the small public interface for the VFS operation implementation in `xfs_file.c`.
