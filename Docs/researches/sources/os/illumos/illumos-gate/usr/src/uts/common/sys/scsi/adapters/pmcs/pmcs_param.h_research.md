# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_param.h

## Purpose
Collects compile-time tunable parameters and fixed sizing constants for the PMCS driver.

## Main Interfaces
- Defines maximum configuration time, max IQ/OQ counts, max ports, expansion depth, control/scratch area sizes, firmware log size/threshold, queue entry size/depth, watchdog interval, forward-progress cadence, inbound/outbound queue numbering, SGL chunk limits, interrupt vector counts, and firmware image names/offsets.
- Establishes the driver's active queue model: nine inbound queues, three outbound queues, and one fatal interrupt vector.

## Dependencies And Relationships
Included early by `pmcs.h` and used by queue allocation, MPI setup, scratch/SMP operations, firmware logging, watchdog, DMA SGL construction, and firmware update code.

## Research Notes
Several values are intentionally aligned with hardware assumptions, especially `PMCS_QENTRY_SIZE`, `PMCS_CONTROL_SIZE`, and the scratch area large enough for maximum SMP request/response payloads.
