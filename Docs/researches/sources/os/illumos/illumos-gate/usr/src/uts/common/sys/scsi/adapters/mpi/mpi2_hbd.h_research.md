# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_hbd.h

## Purpose
Defines the MPI v2 Host Based Discovery action request/reply ABI used by host software to add, remove, or update SAS devices in firmware-managed discovery state.

## Main Interfaces
- Host Based Discovery action messages:
  - `MPI2_HBD_ACTION_REQUEST`
  - `MPI2_HBD_ACTION_REPLY`
- HBD operations:
  - `MPI2_HBD_OP_ADD_DEVICE`
  - `MPI2_HBD_OP_REMOVE_DEVICE`
  - `MPI2_HBD_OP_UPDATE_DEVICE`
- HBD device information flags:
  - virtual device, ATAPI, direct attach, SSP/STP/SMP target and initiator bits, SATA device/host bits
  - device type mask and values for no device, end device, edge expander, and fanout expander
- HBD maximum link-rate encodings:
  - 1.5, 3.0, and 6.0 Gbit/s SAS rates
  - MPI v2.5 12.0 Gbit/s
  - MPI v2.6 22.5 Gbit/s

## Dependencies And Relationships
This header relies on the surrounding MPI base typedefs and pointer macros (`U8`, `U16`, `U32`, `U64`, `MPI2_POINTER`) provided by the MPI include stack. It complements `mpi2_cnfg.h`, whose IO Unit Page 1 includes `MPI2_IOUNITPAGE1_ENABLE_HOST_BASED_DISCOVERY`, and the core `mpi2.h` function-code space, where host discovery is represented by an MPI message function.

## Research Notes
The header identifies itself as `mpi2_hbd.h` version `02.00.04`. The request includes a firmware `DevHandle`, `SASAddress`, parent handle, queue depth, first PHY, port, maximum connection/rate fields, `AdditionalInfo`, and initial arbitration wait time. The reply echoes operation and handle context and returns standard MPI `IOCStatus`/`IOCLogInfo`.

## Notable Risks
- The HBD request directly mutates firmware discovery topology. Incorrect operation, parent handle, SAS address, device-info flags, or rate fields can create stale or incorrect device records.
- The `HbdDeviceInfo` field encodes both role/protocol bits and device-type bits; callers must mask the low bits before interpreting device type.
- MPI v2.5/v2.6 rate values must only be used where firmware supports those link generations.
