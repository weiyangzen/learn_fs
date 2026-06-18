# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sesio.h

## Purpose
Defines user-facing SES enclosure ioctl structures, element types, status values, and control bits.

## Main Interfaces
- `ses_object`: object id, subenclosure id, element type.
- Enclosure element type constants including device, power, fan, thermal, alarm, SCC, UPS, display, SCSI target/initiator, array, SAS expander, and SAS connector.
- Overall enclosure status bits: unrecoverable, critical, noncritical, info.
- `ses_objarg`: object id and four status/control bytes.
- SES common status constants.
- Control bits for common, device, and generic element control bytes.
- Ioctls: legacy `SESIOC_IOCTL_*` and object/status operations `SESIOC_GETNOBJ`, `SESIOC_GETOBJMAP`, `SESIOC_INIT`, `SESIOC_GETENCSTAT`, `SESIOC_SETENCSTAT`, `SESIOC_GETOBJSTAT`, `SESIOC_SETOBJSTAT`.
- `struct ses_ioctl`: raw page access descriptor.

## Dependencies And Relationships
Included by `ses.h` and consumed by SES applications and driver ioctl handlers.

## Research Notes
This is the ABI boundary for enclosure management applications.

## Notable Risks
- Bitfield layout in `ses_object` is compiler/ABI-sensitive.
- Ioctls can change enclosure element state, including identify/fault/device-off controls.
