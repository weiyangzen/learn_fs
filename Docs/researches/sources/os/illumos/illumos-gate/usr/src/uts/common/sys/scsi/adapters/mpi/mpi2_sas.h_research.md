# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_sas.h

## Purpose
Defines MPI v2 SAS-specific status values, SAS device-info bits, SMP passthrough, SATA passthrough, and pre-v2.6 SAS IO Unit Control messages.

## Main Interfaces
- SAS status constants:
  - success, invalid frame, unsupported destination/rate/protocol, STP resource busy, wrong destination, IU length errors, XFER_RDY errors, data length/offset errors, NAK/connection failure, and initiator response timeout.
- Device-info flags:
  - SEP, ATAPI, LSI, direct attach, SSP/STP/SMP target, SATA device, SSP/STP/SMP initiator, SATA host, and device type mask for no device/end device/edge expander/fanout expander.
- SMP passthrough:
  - `MPI2_SMP_PASSTHROUGH_REQUEST`
  - `MPI2_SMP_PASSTHROUGH_REPLY`
  - immediate-response flag and SAS status reporting.
- SATA passthrough:
  - `MPI2_SATA_PT_SGE_UNION`
  - `MPI2_SATA_PASSTHROUGH_REQUEST`
  - `MPI2_SATA_PASSTHROUGH_REPLY`
  - command/status FIS fields, data lengths, transfer count, and flags for diagnostic execution, FPDMA, DMA, PIO, vendor-specific, read, and write.
- SAS IO Unit Control:
  - `MPI2_SAS_IOUNIT_CONTROL_REQUEST`
  - `MPI2_SAS_IOUNIT_CONTROL_REPLY`
  - operations for persistent cleanup, PHY link/hard reset, error-log clearing, primitive send, discovery, port-select signal, remove device, mapping lookup, IOC parameter set, fast-path control, NCQ control, and product-specific operations.

## Dependencies And Relationships
Uses core MPI SGE unions and scalar typedefs. MPI v2.6 replaces the SAS-specific IO Unit Control message with the generic `MPI26_IOUNIT_CONTROL_*` messages in `mpi2_ioc.h`; this header remains relevant for MPI v2.0/v2.5 products and passthrough operations.

## Research Notes
The version is `02.00.10`. SGE union comments are important: MPI v2.5 restricts some passthrough paths to IEEE 64-bit elements, while MPI v2.0 allows MPI and IEEE simple/chain variants. `MPI2_SATA_PT_REQ_PT_FLAGS_FPDMA` is explicitly MPI v2.6-and-newer even though the rest of the SAS IO Unit Control section is pre-v2.6.
