# File Research: sources/virtualization/libblockdev/src/plugins/smart/smartmontools.c

This file implements the SMART plugin backend using the external `smartctl` command from smartmontools. It parses `smartctl --json` output into the public `BDSmartATA` and `BDSmartSCSI` structs.

Dependency handling:
- Requires `smartctl >= 7.0`.
- Uses `check_deps()` with a regex matching `smartctl ([\d\.]+) .*`.
- `_smart_close_plugin()` clears the cached dependency bitset.
- `bd_smart_is_tech_avail()` treats all SMART tech/mode combinations as supported if smartctl is available.
- `bd_smart_check_deps()` delegates to `bd_smart_is_tech_avail()`.

Error parsing:
- `get_error_message_from_exit_code()` explains smartctl low-bit failures for command parse, device open/identify, and SMART command/checksum problems.
- `parse_smartctl_error()` parses stdout JSON, validates `json_format_version`, extracts error messages, and treats only exit status bits `0x01`, `0x02`, and `0x04` as hard failures.
- This means health-related smartctl status bits outside `0x07` can still produce usable parsed data.

ATA parsing:
- `parse_ata_smart_attributes()` reads the `ata_smart_attributes.table` array and fills ID, name, normalized values, threshold, failure state, raw value/string, and flags.
- `lookup_well_known_attr()` validates smartmontools attribute names against `well_known_attrs`, assigns trusted libatasmart-style names, and attempts unit-specific pretty-value conversion.
- Millisecond values are parsed from smartctl time strings when possible.
- Temperature values are parsed from Celsius strings and converted to millikelvin.
- Unsupported units fall back to unknown.
- `parse_ata_smart()` reads support/enabled state, overall status, offline collection status, self-test status/polling, capabilities, attribute table, power-on time, power-cycle count, and current temperature.

SCSI parsing:
- `parse_scsi_smart()` reads SMART support/enabled/health status, SCSI informational exception fields, temperature warning, current/trip temperature, background scan status/progress/counts, start-stop/load-unload counters, grown defect list, read/write error counter logs, processed byte totals, and power-on time.
- ASC/ASCQ values are mapped into the public `BDSmartSCSIInformationalException` enum, including `0x0b` warnings and `0x5d` impending failure categories.
- Background scan status values are mapped to public enum values, with unknown values copied through.

Operational functions:
- `bd_smart_ata_get_info()` runs `smartctl --info --health --capabilities --attributes --json <device>`.
- `bd_smart_ata_get_info_from_data()` parses a JSON blob supplied by the caller, unlike the libatasmart backend which parses libatasmart binary blob data.
- `bd_smart_scsi_get_info()` runs `smartctl --info --health --attributes --log=error --log=background --json <device>`.
- `bd_smart_set_enabled()` runs `smartctl --json --smart=on/off <device>`.
- `bd_smart_device_self_test()` maps libblockdev self-test ops to smartctl `--abort` or `--test=...`.

Important behavior and caveats:
- `extra` arguments are passed through the exec utility, allowing smartctl options such as `--device=`.
- The backend depends on JSON key stability and is intentionally tolerant of many optional missing sections.
- Hard parsing errors are returned as `BD_SMART_ERROR_INVALID_ARGUMENT`.
- SCSI parsing currently ignores the `error` parameter and does not fail for missing optional sections.
- Temperature conversion here stores Celsius plus 273, while ATA attribute pretty values use millikelvin conversion logic.
