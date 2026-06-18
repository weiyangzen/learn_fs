# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_proto.h

## Purpose
Declares PMCS driver functions and debug-printing levels used across attach/setup, firmware, queueing, discovery, SATA/SAS/SMP operations, SCSA integration, recovery, diagnostics, and iport/PHY lifetime management.

## Main Interfaces
- `pmcs_prt_level_t` and `pmcs_prt()` gate debug/error output by debug mask.
- Prototypes cover target assignment/removal, scratch acquisition, work allocation/tag lookup, aborts, SSP TMF, SATA NCQ abort, interrupt handlers, device registration, endian transforms, status/name helpers, WWN conversions, setup/MPI start/stop, firmware update/flash, echo test, PHY start/stop, iport target maps, SAS diagnostics, register dumps, resets, discovery, interrupt coalescing, IOMB status checks, SATA identify/work, DMA setup, FMA checks, NVMD access, completion processing, queue flushing, recovery, iport reference management, phymap callbacks, PHY locking/refcounts, worker thread, fatal handling, SMP serialization, SM-HBA PHY property updates, and firmware log gathering.

## Dependencies And Relationships
Depends on `pmcs_hw_t`, `pmcs_phy_t`, `pmcs_xscsi_t`, `pmcwork_t`, `pmcs_iport_t`, `pmcs_fw_hdr_t`, `pmcs_nvmd_type_t`, and related PMCS data types declared by other PMCS headers.

## Research Notes
This file is a useful index to the implementation modules: almost every major operational area of the PMCS driver has a cross-module prototype here.
