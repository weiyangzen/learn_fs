# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tspriocntl.h

## Purpose
Priority-control definitions for the time-sharing scheduler class.

## Main Interfaces
- Defines `tsparms_t` with user priority limit and user priority.
- Defines `tsinfo_t` with maximum user priority.
- Defines `TS_NOCHANGE`.
- Defines key IDs `TS_KY_UPRILIM` and `TS_KY_UPRI`.
- Defines admin payloads `tsadmin32_t` and `tsadmin_t` for dispatch table management.
- Defines admin commands `TS_GETDPSIZE`, `TS_GETDPTBL`, and `TS_SETDPTBL`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/thread.h`; relies on `struct tsdpent` from the TS scheduler class. Used by `priocntl` administration for the time-sharing class.

## Research Notes
The 32-bit and native admin structures differ in how dispatch table pointers are represented, so consumers must use the correct command ABI.
