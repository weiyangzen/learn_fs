# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_mpi.h

## Purpose
Defines PMCS Message Passing Interface table offsets, firmware version extraction, queue configuration-table layout, general status table offsets, event queue assignment macros, log buffer registers, and fatal error controls.

## Main Interfaces
- MPI configuration offsets include signature, interface revision, firmware version, max outstanding I/O, max S/G and device handles, queue counts, GST/IQ/OQ table offsets, queue-depth information, event queues, NCQ queues, customization settings, log buffers, and fatal-error registers.
- Macros extract firmware type/variant/major/minor/micro/revision and build comparable version values.
- `PMCS_MPI_EVQSET()` and `PMCS_MPI_NCQSET()` program per-PHY outbound queues for SAS events and SATA NCQ notification.
- GST macros expose MPI state, queue freeze, heartbeats, PHY info, and recoverable error info.
- IQC/OQC macros describe per-queue configuration table slots and decode depth, entry size, interrupt coalescing count/timer/vector, and queue parameters.

## Dependencies And Relationships
Used during `pmcs_start_mpi()`, queue setup, interrupt configuration, firmware logging, heartbeat/watchdog, and fatal error handling.

## Research Notes
This header is the bridge between the driver's queue-memory allocations and the firmware's MPI configuration tables.
