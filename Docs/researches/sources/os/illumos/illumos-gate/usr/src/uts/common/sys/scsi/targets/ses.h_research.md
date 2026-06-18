# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ses.h

## Purpose
Private header for the SCSI Enclosure Services target driver, including SES/SAF-TE/SEN soft-state, object mapping, command vectors, retries, timeouts, debugging, and common command helpers.

## Main Interfaces
- SAF-TE READ/WRITE BUFFER command IDs.
- Convenience macros for SCSI packet/status/buffer/device access.
- `encvec`: enclosure operation vector for init, enclosure status, and object status get/set.
- `enctyp`: enclosure type enum for SES, SAF-TE, and SEN.
- `encobj`: enclosure object mapping entry.
- `struct ses_softc`: main driver soft-state with type/vector, object map, enclosure status, SCSI device, request sense resources, special buffer, restart timeout, open/suspend/present state, retries, devid, and embedded uscsi/request-sense buffers.
- Debug and retry macros, timeout constants, callback action codes.
- Kernel functions: `ses_log`, `ses_runcmd`, `ses_uscsi_cmd`.

## Dependencies And Relationships
Includes `sys/note.h` and `sys/scsi/targets/sesio.h`. Depends on SCSA, buffer, uscsi, sense, and DDI types supplied by C files/include context.

## Research Notes
The header contains Warlock annotations documenting protection by `scsi_device::sd_mutex` and special-buffer CV ownership.

## Notable Risks
- SES object state and special buffer fields are shared across ioctl and command paths.
- Retry weights intentionally differ for command, busy, and sense cases.
- SAF-TE and SES command semantics coexist in one driver abstraction.
