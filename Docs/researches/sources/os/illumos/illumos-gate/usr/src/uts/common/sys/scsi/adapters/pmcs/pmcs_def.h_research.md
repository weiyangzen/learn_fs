# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_def.h

## Purpose
Defines PMCS driver-wide data types, PHY discovery state, work-item state, firmware header format, tag architecture, work scheduling macros, tracing records, firmware event-log formats, and receptacle metadata.

## Main Interfaces
- `pmcs_dtype_t` classifies PHY contents as empty, SATA, SAS, expander, or new.
- `pmcs_phy_t` represents a physical or discovered PHY node, including tree links, device handle, link/recovery state, SAS address, iport/target back-pointers, port phymasks, SMP routing attributes, and cached SMP report/discover responses.
- `pmcwork_t` tracks one firmware command/work item, with locks, wait CV, tag, owning PHY/target, timeout, state, timestamps, abort tag, and last-use diagnostics.
- Tag macros split 32-bit firmware tags into done/non-IO/type/serial/index fields.
- Work flags and `SCHEDULE_WORK()`/`WORK_SCHEDULED()` encode offlevel tasks such as discovery, abort handling, spinup release, SATA work, queue running, DMA chunk addition, recovery, deregistration, and register dump.
- `pmcs_fw_hdr_t`, `pmcs_tbuf_t`, `pmcs_fw_event_hdr_t`, and `pmcs_fw_event_entry_t` describe firmware image and logging formats.

## Dependencies And Relationships
Uses `pmcs_hw_t`, `pmcs_iport_t`, `pmcs_xscsi_t`, and SAS/SMP types declared through `pmcs.h` includes. It is foundational for discovery, queueing, firmware update, event logging, and diagnostic code.

## Research Notes
The extensive comments around queue memory layout and tag architecture are important: they explain how host memory control areas, firmware tags, and interrupt-side completion ownership fit together.
