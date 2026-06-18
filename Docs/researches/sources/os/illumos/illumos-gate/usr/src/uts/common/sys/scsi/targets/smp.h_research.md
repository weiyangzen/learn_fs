# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/smp.h

## Purpose
Private target-driver header for SAS SMP devices.

## Main Interfaces
- Open states: `SMP_CLOSED`, `SMP_SOPENED`, `SMP_EXOPENED`.
- `smp_state_t`: SMP device pointer, mutex, open flag, condition variable, and busy flag.
- Soft-state sizing and retry constants.
- Transfer buffer flags: `SMP_FLAG_REQBUF`, `SMP_FLAG_RSPBUF`, `SMP_FLAG_XFER`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/scsi/scsi.h`; related to the user SMP ioctl ABI in `impl/usmp.h`.

## Research Notes
Kernel-only state is guarded by `_KERNEL`.

## Notable Risks
- Open/busy state must be serialized to prevent overlapping SMP management operations.
- SMP commands can alter or query SAS expander topology.
