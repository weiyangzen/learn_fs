# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sgendef.h

## Purpose
Private header for the generic SCSI target driver, defining ioctls, state, binding database structures, flags, retries, and error statistics.

## Main Interfaces
- Ioctls: `SGEN_IOC_READY`, `SGEN_IOC_DIAG`.
- Kernel diagnostics levels `SGEN_DIAG1` through `SGEN_DIAG3`.
- `struct sgen_errstats`: kstat counters for transport, restart, incomplete, autosense, sense, recoverable, no-sense, and unrecoverable errors.
- `sgen_state_t`: scsi device, uscsi command, command/sense buffers and packets, flags, ARQ, diagnostics, restart timeout, and kstats.
- State macros for open, suspended, busy, and exclusive flags.
- Binding database nodes for inquiry strings and device types.
- Retry/busy timeout and callback action constants.

## Dependencies And Relationships
Includes kernel synchronization, kstat, buf, and `sys/scsi/scsi.h`. Uses `uscsi_cmd` and SCSA packet/sense machinery.

## Research Notes
The driver supports binding by inquiry vendor/product strings or SCSI device type from configuration properties.

## Notable Risks
- Generic SCSI passthrough can expose broad device control.
- Busy/open/exclusive flag macros assume external synchronization by the driver.
