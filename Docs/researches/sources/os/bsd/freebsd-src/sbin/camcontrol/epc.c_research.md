# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/epc.c

## Purpose
Implements ATA Extended Power Conditions control and reporting for ATA/SATL devices.

## Main Elements
- Maps EPC commands, power conditions, restore value sources, power sources, and flags.
- `epc_print_pcl_desc()`: formats one ATA power condition log descriptor.
- `epc_list()`: reads ATA power condition log pages and prints Idle A/B/C and Standby Y/Z state.
- `epc_getmode()`: reads identify data and supported capabilities log, reports APM/EPC support, low-power standby support, current power state, wait mode, and hold state.
- `epc_set_features()`: builds ATA SET FEATURES EPC subcommands for timer/state/goto/restore/enable/disable/source.
- `epc()`: parses options, validates action-specific required arguments, checks device type, and dispatches.

## Dependencies And Integration
Uses CAM ATA command construction, ATA identify/log structures, SATL handling, and shared `get_device_type()` / `get_ata_status()` helpers.

## Risk Notes
Some actions change drive power state or persistent EPC timers. The command is restricted to ATA and SATL devices to avoid invalid SCSI/NVMe use.
