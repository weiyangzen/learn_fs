# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ra.h

## Purpose
Defines the MPI v2 RAID Accelerator request, reply, and control-block layouts. This header exposes a small product-specific accelerator path around a controller-owned RAID accelerator CDB.

## Main Interfaces
- `MPI2_RAID_ACCELERATOR_CONTROL_BLOCK`: generic control block with reserved header words and a variable `RaidAcceleratorCDB` payload.
- `MPI2_RAID_ACCELERATOR_REQUEST`: command message containing a 64-bit control-block address and DMA engine number.
- `MPI2_RAID_ACCELERATOR_REPLY`: error/status reply with `IOCStatus`, `IOCLogInfo`, and three product-specific data words.

## Dependencies And Relationships
Depends on MPI scalar and pointer typedefs from the shared MPI header set. It is adjacent to `mpi2_raid.h`: the accelerator interface is separate from normal integrated RAID action messages, but both are controller firmware ABI definitions for RAID-related facilities.

## Research Notes
The version is `02.00.01`; the content is intentionally minimal. Most semantics are left to the firmware/product-specific RAID accelerator CDB, so this header mainly matters for exact DMA address, engine-selection, and reply-status packing.
