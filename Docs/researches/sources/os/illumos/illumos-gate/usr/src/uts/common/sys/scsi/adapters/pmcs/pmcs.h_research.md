# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs.h

## Purpose
Principal private header for the PMC-Sierra PM8001/8x6G SAS/SATA HBA driver. It gathers the PMCS subheaders and defines the target, LUN, iport, DMA chunk, interrupt coalescing, completion-thread, and HBA soft-state structures.

## Main Interfaces
- `pmcs_xscsi_t` is target state: SATA flags, reset/recovery state, queue depths, command counters, wait/active/special queues, tag map, capacity, unit address, dtype, LUN list, and SMP device pointer.
- `pmcs_lun_t` binds a SCSI LUN number and wire-format LUN to the target and `scsi_device`.
- `pmcs_iport_t` is per-iport state, including phymap unit-address state, target map, target softstate, PHY list, and serialized SMP request state.
- `pmcs_hw_t` is the central HBA state: DDI handles, PCI/register windows, DMA queues, MPI offsets, scratch/FW log/register-dump memory, interrupts, PHY discovery tree, work pools, SCSA/SMP transports, target arrays, completion queues, interrupt coalescing, firmware metadata, and FMA receptacle data.
- `pmcs_io_intr_coal_t`, `pmcs_cq_thr_info_t`, `pmcs_cq_info_t`, and `pmcs_iocomp_cb_t` support interrupt coalescing and deferred completion processing.

## Dependencies And Relationships
Includes SCSA, SMP, SAS, DDI/FMA, MDI, byteorder, bitmap, queue, and SPC-3 type headers, then pulls in `pmcs_param.h`, `pmcs_reg.h`, `pmcs_mpi.h`, `pmcs_iomb.h`, `pmcs_sgl.h`, `ata.h`, `pmcs_def.h`, `pmcs_proto.h`, `pmcs_scsa.h`, and `pmcs_smhba.h`.

## Research Notes
This header shows the driver's core architecture: firmware MPI queues feed work structures; discovery builds a PHY tree; iports expose phymap-derived ports; and SCSA/SMP targets hang off iport target maps.
