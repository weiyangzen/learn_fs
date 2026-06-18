# File Research: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.h

## Role
Internal header for the LVM VDO stats helper.

## Exposed Functions
- `get_stat_val_double()`
- `get_stat_val64()`
- `get_stat_val64_default()`
- `vdo_get_stats_full()`

## Notes
Although the file is small, it exposes parser helpers as non-static functions for use by other LVM plugin implementation files. It includes only GLib and guards itself with `BD_VDO_STATS`.
