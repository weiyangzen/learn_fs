# File Research: sources/local-fs/xfsprogs/libxfs/xfs_errortag.h

## Purpose
Defines XFS error-injection tag identifiers and the macro table used to generate error-tag metadata.

## Main Contents
- Numeric `XFS_ERRTAG_*` constants from `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` set to 48.
- `XFS_RANDOM_DEFAULT`, the default randomization divisor for error injection.
- Optional `XFS_ERRTAGS` macro expansion table, enabled when includers define `XFS_ERRTAG(name, knob, default)`.

## Integration
The header supports two include modes: direct inclusion for constants, or macro-driven inclusion to generate tables of sysfs/debug knobs and default injection frequencies. `XFS_ERRTAG_EXCHMAPS_FINISH_ONE` is used by `xfs_exchmaps_finish_one()` to inject failures into exchange-mapping deferred work.

## Risks and Notes
The numeric constants are expected to remain consecutive because arrays are sized from the maximum. The removed drop-writes tag remains reserved so invalid historical values can still be rejected. Adding a tag requires updating both the numeric list and the macro table consistently.
