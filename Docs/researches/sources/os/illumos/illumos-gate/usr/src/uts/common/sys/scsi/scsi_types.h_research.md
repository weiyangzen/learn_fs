# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_types.h

## Purpose
Central SCSI subsystem type/include aggregator.

## Main Interfaces
- Defines `opaque_t` as `void *` if not already defined.
- Includes base system types and parameters.
- Under `_KERNEL`, includes DDI, devops, sunddi, stat, NDI, and devctl headers.
- Includes SCSI params, address, packet, device config, control, resource, autoconf, watch, FMA, generic command/status/message/mode, and implementation types.

## Dependencies And Relationships
This is the main include stack behind `scsi.h` and most SCSI target/HBA headers.

## Research Notes
It intentionally blends generic SCSI protocol headers with illumos implementation-specific SCSI headers.

## Notable Risks
- Broad include fan-out means changes here can affect many kernel compilation units.
- User-visible and kernel-only portions are interleaved through `_KERNEL` guards.
