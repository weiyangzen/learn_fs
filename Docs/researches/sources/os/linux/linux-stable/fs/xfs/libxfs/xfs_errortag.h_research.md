# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_errortag.h

## Purpose

`xfs_errortag.h` defines the central list of XFS error injection tags and the macro table used to generate sysfs knobs or other tag metadata. It supports two include modes:

- Bare include: defines `XFS_ERRTAG_*` numeric constants.
- Include with `XFS_ERRTAG` defined: defines `XFS_ERRTAGS`, a table-like macro expansion invoking the caller's `XFS_ERRTAG(symbol, knob, default)` for every tag.

## Tags and Numbering

The numeric constants are consecutive from `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` equal to 48. Consecutive numbering matters because arrays are sized by the maximum value.

The tag set covers:

- Inode flush paths (`IFLUSH_1` through `IFLUSH_6`).
- Directory/attribute/btree/bmap/rmap/refcount paths.
- Allocation group and metadata reservations.
- IO error injection for log, read, completion, direct write, and buffer IO.
- Scrub/repair forcing and summary recalculation.
- Extent count reduction and minlen allocation forcing.
- Delays for writeback/write.
- Exchange mappings, metadata-file reservation, zero range, and zoned-device reset paths.

`XFS_ERRTAG_DROP_WRITES` is retained numerically even though drop-writes support was removed, so invalid values can still be rejected predictably by error-tag parsing code.

## Default Frequencies

`XFS_RANDOM_DEFAULT` is 100. The macro table gives each knob a default random factor. Some tags default to always or near-always (`1`), some to low-frequency IO-error rates (`XFS_RANDOM_DEFAULT/10`), and delay knobs use millisecond-like values (`3000`).

## Notable Consumers

Within this group, `xfs_exchmaps_finish_one` checks `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`. Elsewhere in XFS, the tags are referenced by `XFS_TEST_ERROR` call sites and by the error-injection sysfs plumbing generated from `XFS_ERRTAGS`.

## Implementation Notes

The include guard is intentionally unusual: `#if !defined(__XFS_ERRORTAG_H_) || defined(XFS_ERRTAG)`. This permits a second include with `XFS_ERRTAG` defined to regenerate the macro table even after the bare definitions have been included once.
