# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi.h

## Purpose
Top-level global include for the illumos SCSI subsystem.

## Main Interfaces
- Includes `sys/scsi/scsi_types.h`.

## Dependencies And Relationships
Acts as the simple public entry point used by SCSI target and HBA headers to pull in the common SCSA include stack.

## Research Notes
No declarations beyond the include wrapper.

## Notable Risks
- Changes to `scsi_types.h` propagate to any consumer including this top-level header.
