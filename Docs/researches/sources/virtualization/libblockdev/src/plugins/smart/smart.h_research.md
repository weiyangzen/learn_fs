# File Research: sources/virtualization/libblockdev/src/plugins/smart/smart.h

This public header defines the SMART plugin API, public structs, enums, and exported functions.

Public error and tech enums:
- `BDSmartError`: technology unavailable, general failure, invalid argument.
- `BDSmartTech`: ATA and SCSI.
- `BDSmartTechMode`: info and self-test modes.

ATA API model:
- Defines offline data collection statuses and capability bits.
- Defines ATA self-test statuses.
- Defines miscellaneous ATA SMART capability bits.
- Defines pretty-value units: unknown, none, milliseconds, sectors, millikelvin, small percent, percent, and megabytes.
- Defines ATA attribute flags mirroring SMART attribute flag bits.

`BDSmartATAAttribute` stores:
- Attribute ID.
- Backend-specific `name`.
- Trusted normalized `well_known_name`, or `NULL`.
- Normalized value, worst, threshold.
- Past/current failure flags.
- Raw 64-bit value.
- Flag bitmask.
- Parsed pretty value, unit, and printable string.

`BDSmartATA` stores:
- SMART support/enabled and overall status.
- Offline data collection status/capabilities.
- Self-test status, remaining percent, and polling hints.
- SMART capabilities.
- NULL-terminated ATA attribute vector.
- Power-on time in minutes, power-cycle count, and temperature in Kelvin.

SCSI API model:
- `BDSmartSCSIInformationalException` enumerates SCSI informational exception ASC/ASCQ categories, including warnings and impending failure classes.
- `BDSmartSCSIBackgroundScanStatus` enumerates background scan states.
- `BDSmartSCSI` stores support/enabled/status, informational exception fields, background scan metrics, error counters, cycle counters, grown defect list, power-on time, and temperature fields.

Exported functions:
- Boxed free/copy helpers for ATA, ATA attributes, and SCSI structs.
- Plugin lifecycle/dependency functions: `bd_smart_check_deps()`, `bd_smart_init()`, `bd_smart_close()`, `bd_smart_is_tech_avail()`.
- Operational calls: ATA info from device or data, SCSI info, SMART enable/disable, and self-test execution.

Research relevance:
- This header is the authoritative contract for what the two SMART backends must populate.
- Some fields are explicitly backend-dependent; comments note that some are only supported by smartmontools.
- Temperature is documented as Kelvin, while internal backends convert from Celsius or millikelvin.
