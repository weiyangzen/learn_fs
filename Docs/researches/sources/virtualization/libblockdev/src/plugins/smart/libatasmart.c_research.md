# File Research: sources/virtualization/libblockdev/src/plugins/smart/libatasmart.c

This file implements the SMART plugin backend using `libatasmart`. It supports ATA SMART information retrieval and ATA self-test triggering, but explicitly reports SCSI SMART and SMART enable/disable as unavailable for this backend.

Key entry points:
- `_smart_close_plugin()` is a no-op backend close hook.
- `bd_smart_check_deps()` always returns `TRUE` because the backend is linked against libatasmart rather than checking an external utility.
- `bd_smart_is_tech_avail()` returns available for `BD_SMART_TECH_ATA`, unavailable for `BD_SMART_TECH_SCSI`, and unavailable for unknown technologies.
- `bd_smart_ata_get_info()` opens a device with `sk_disk_open()`, parses SMART data, and returns a populated `BDSmartATA`.
- `bd_smart_ata_get_info_from_data()` parses libatasmart blob data through `sk_disk_set_blob()`.
- `bd_smart_scsi_get_info()` always fails with `BD_SMART_ERROR_TECH_UNAVAIL`.
- `bd_smart_set_enabled()` always fails because libatasmart does not expose that control here.
- `bd_smart_device_self_test()` maps libblockdev self-test operations to `SkSmartSelfTest` and calls `sk_disk_smart_self_test()`.

The central conversion path is `parse_sk_data()`: it reads SMART data, asks libatasmart for overall health, parses status/capability fields, computes power-on time and power-cycle count, parses attributes into `BDSmartATAAttribute`, and terminates the attribute vector with `NULL`.

Attribute parsing:
- `parse_attr_cb()` copies libatasmart parsed attributes into libblockdev fields.
- Raw values are packed from six raw bytes into a 64-bit integer.
- `print_value()` mirrors a private libatasmart formatting helper for human-readable values.
- Units are translated from `SkSmartAttributeUnit` to `BDSmartATAAttributeUnit`.
- Attribute failure state is inferred from normalized value/worst versus threshold.
- If built with `HAVE_DRIVEDB_H`, the backend uses `drivedb_lookup_drive()` and `well_known_attrs` to distrust attributes whose smartmontools drive DB name does not match libblockdev’s whitelist.

Temperature handling is conservative: `calculate_temperature()` checks attributes 194 and 190, requiring millikelvin units for those IDs, and returns zero if no recognized temperature attribute is present. `parse_sk_data()` stores temperature as Kelvin after dividing millikelvin by 1000.

Important behavior and caveats:
- `extra` arguments are ignored in this backend, unlike the smartmontools backend.
- Several ATA fields are marked TODO or zero-filled, including automatic offline data collection, offline capabilities, and broader SMART capabilities.
- `bd_smart_ata_get_info_from_data()` leaks the opened `SkDisk` if `sk_disk_set_blob()` fails because it returns without `sk_disk_free(d)`.
- `bd_smart_scsi_get_info()` returns `FALSE` from a pointer-returning function; this works as `NULL` but is stylistically imprecise.
- Errors use locale-neutral `strerror_l(errno, _C_LOCALE)` via `smart-private.h`.
