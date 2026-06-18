# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/types.h

## Purpose
Aggregates implementation-specific SCSI subsystem includes.

## Main Interfaces
- Kernel include wrapper for common kernel, buffer, ioctl, SCSA service, transport, SMP transport, and SAS headers.
- Always includes `sys/scsi/impl/uscsi.h`.

## Dependencies And Relationships
Included by `scsi_types.h` as the final Sun/illumos implementation-specific SCSI layer. Under `_KERNEL`, it pulls in `transport.h`, `smp_transport.h`, and `scsi_sas.h`.

## Research Notes
This header defines no new data structures itself; it centralizes implementation include dependencies.

## Notable Risks
- Because it is pulled into broad SCSI include stacks, adding dependencies here can increase compile coupling across many drivers.
