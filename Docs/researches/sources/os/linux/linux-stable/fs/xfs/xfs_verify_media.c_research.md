# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.c

## Purpose

Implements the XFS media verification ioctl. It reads device ranges to detect media/protection errors and optionally reports data loss through health monitoring and reverse mapping.

## Main Responsibilities

- Validates user-supplied verification request fields.
- Selects data, log, or realtime target device.
- Verifies logical-sector-aligned disk ranges with synchronous read bios.
- Chooses verification I/O size, up to a requested/user-limited maximum.
- Reports media, protection, and I/O failures to health monitoring.
- Uses reverse mapping to notify affected inodes of lost file data.
- Updates the request start address to the verified progress point.

## Important Invariants

- Start and end disk addresses must align to the target logical sector size.
- End address is exclusive and is clamped to device size.
- Errors before any verified byte are returned to userspace.
- Only protection, medium, and generic I/O failures are treated as data-loss reports.
- Rmap-based file loss reporting requires rmapbt support.
- Verification can be interrupted by fatal signals between bios.

## Dependencies

Uses Linux bios/folios, XFS btrees, rmap/rtrmap, allocation groups, realtime groups, inode lookup, healthmon, and ioctl copy helpers.

## Research Notes

This file is diagnostic and reporting code, not repair code. Its most important behavior is mapping physical verification failures back to affected file ranges when rmap metadata exists.
