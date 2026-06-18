# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.c

## Purpose

Implements the XFS GETFSMAP ioctl, reporting physical storage mappings across data, log, and realtime devices. It translates internal allocation/reverse-map metadata into generic `struct fsmap` records for userspace.

## Main Responsibilities

- Converts between userspace `fsmap` byte units and internal basic-block units.
- Converts owners between fsmap owner IDs and XFS rmap owner IDs.
- Tracks query state in `struct xfs_getfsmap_info`.
- Formats mapping records and synthetic gap records.
- Detects shared extents via refcount btrees when reflink is enabled.
- Queries data device mappings using:
  - rmapbt when available and caller has `CAP_SYS_ADMIN`
  - bnobt free-space records as fallback
- Queries external log device by fabricating a log-owner mapping.
- Queries realtime device using:
  - rtbitmap fallback for non-zoned/non-rmap queries
  - realtime rmapbt for privileged rmap-backed queries
- Handles zoned internal realtime layout by reporting the address gap before rtstart as filesystem-owned.
- Validates devices and low/high keys.
- Sorts device handlers and iterates matching devices.
- Allocates an internal bounded buffer for ioctl output and batches copyout to userspace.
- Implements continuation semantics by using the last returned record as the next low key.
- Sets `FMR_OF_LAST` on the final returned record when the query is complete.

## Important Invariants

- Rmap-backed queries are only used when rmapbt exists and caller has admin capability.
- Without rmapbt, data-device fsmap can report free/unknown space but not full owner detail.
- Low keys with nonzero length mean “continue after this previous record”.
- Shareable file-data mappings continue by bumping owner offset; unshareable mappings continue by bumping physical position.
- Synthetic gaps are emitted when the next known mapping starts after `next_daddr`.
- Internal buffers avoid copying to userspace while filesystem metadata locks are held.
- High keys must have zero or all-ones length; special-owner or extent-map keys cannot carry arbitrary offsets.

## Dependencies

- Uses rmap btree, refcount btree, bnobt, rtbitmap, realtime rmap/refcount btrees, perag and rtgroup iteration.
- Uses empty transactions for recursive buffer locking while querying metadata.
- Uses Linux `fsmap` ABI definitions.

## Research Notes

This file is a complex translation layer. Its key value is hiding XFS’s per-AG/per-rtgroup metadata layout behind a single ordered physical mapping API while preserving continuation, gap reporting, sharing flags, and multi-device behavior.
