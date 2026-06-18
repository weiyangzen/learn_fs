# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.h

## Purpose

Declares the XFS media verification ioctl entry point.

## Main Responsibilities

- Forward-declares `struct xfs_verify_media`.
- Declares `xfs_ioc_verify_media`.

## Important Invariants

- Keeps the ioctl implementation interface isolated from callers.

## Dependencies

Depends on `struct file` and the UAPI media verification structure.

## Research Notes

Small public-private header for wiring ioctl dispatch to `xfs_verify_media.c`.
