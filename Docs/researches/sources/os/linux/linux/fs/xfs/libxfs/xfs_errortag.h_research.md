# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_errortag.h

## Purpose

Defines XFS error injection tag numbers and the X-macro table used to generate sysfs/debug error injection knobs and default randomization factors for fault testing.

## Main Interfaces

- Numeric constants: `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` as the array/count bound.
- Default factor: `XFS_RANDOM_DEFAULT`.
- X-macro table: `XFS_ERRTAGS` when the including file defines `XFS_ERRTAG`.

## Control Flow And Behavior

The header supports two include modes. A normal include exposes all `XFS_ERRTAG_*` constants. An include with `XFS_ERRTAG` defined emits `XFS_ERRTAGS`, which expands one row per error injection knob with the symbolic suffix, sysfs knob name, and default randomization factor.

The tags are explicitly documented as consecutive because arrays are sized from the maximum. Removed drop-writes support keeps its numeric definition so attempts to configure that old tag can be rejected as invalid elsewhere.

## State And Data Structures

The file is a macro catalog, not runtime state. It maps error scenarios such as inode flush faults, DA read failures, btree checks, AG header reads, deferred bmap/rmap/refcount steps, quota/metafile reservation failures, writeback delays, exchange-mapping finish failures, and zone reset injection to stable numeric ids and knob names.

## Dependencies

Consumed by XFS error injection code and by call sites using `XFS_TEST_ERROR`, including exchange-mapping code for `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`.

## Risks And Invariants

- Tag numbers must remain consecutive and `XFS_ERRTAG_MAX` must remain one past the last tag.
- Existing tag values are part of debug/test interface expectations and should not be renumbered casually.
- X-macro users depend on each row having exactly suffix, knob name, and default factor.
