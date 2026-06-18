# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/zone.c

## Purpose
Implements SCSI ZBC and ATA ZAC shingled-media zone commands for `camcontrol`, including zone reporting and zone-management operations.

## Main Elements
- Command maps: translate user names such as `reportzones`, `close`, `finish`, `open`, and `rwp` to ZBC/ZAC service actions.
- Report filters and print modes: support all/empty/open/closed/full/etc. filters and normal/summary/script output.
- `zone_rz_print()`: decodes report-zone headers/descriptors in SCSI big-endian or ATA little-endian form, prints zone metadata, and signals whether more data is needed.
- `zone()`: parses command options, detects device type, builds SCSI ZBC or ATA ZAC/NCQ commands, sends the CCB, loops for multi-buffer reports, and frees resources.

## Dependencies And Integration
Uses CAM, SCSI, ATA command builders, `get_device_type()`, and `build_ata_cmd()` from `camcontrol` shared code. Handles both direct SCSI devices and ATA/SATL devices.

## Risk Notes
Report pagination depends on `next_start_lba` from the last decoded descriptor. ATA NCQ and non-NCQ paths encode parameters differently, so command construction must stay aligned with ZAC command definitions.
