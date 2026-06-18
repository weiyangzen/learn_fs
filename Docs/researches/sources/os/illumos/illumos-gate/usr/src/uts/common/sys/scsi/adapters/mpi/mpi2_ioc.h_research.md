# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ioc.h

## Purpose
Defines the Fusion-MPT MPI v2 IOC, port, event, firmware download/upload, image-header, power-management, and MPI v2.6 IO Unit Control wire formats. This is a vendor ABI header for SAS/SCSI/NVMe-capable LSI/Avago/Broadcom controllers, not normal illumos driver logic.

## Main Interfaces
- IOC initialization:
  - `MPI2_IOC_INIT_REQUEST`, `MPI2_IOC_INIT_REPLY`
  - `MPI2_IOC_INIT_RDPQ_ARRAY_ENTRY`
  - who-initialized values, version masks, RDPQ array mode, reply queue depth minimum, and MPI v2.6 NVMe SGL format flag.
- Controller/port discovery:
  - `MPI2_IOC_FACTS_REQUEST`, `MPI2_IOC_FACTS_REPLY`
  - `MPI2_PORT_FACTS_REQUEST`, `MPI2_PORT_FACTS_REPLY`
  - `MPI2_PORT_ENABLE_REQUEST`, `MPI2_PORT_ENABLE_REPLY`
  - IOC exception bits, protocol flags, capability bits, product-family references, and SAS/FC/iSCSI/tri-mode port types.
- Event framework:
  - `MPI2_EVENT_NOTIFICATION_REQUEST`, `MPI2_EVENT_NOTIFICATION_REPLY`
  - `MPI2_EVENT_ACK_REQUEST`, `MPI2_EVENT_ACK_REPLY`
  - event numbers for log/state/reset, SAS device/initiator/topology/enclosure, integrated RAID, GPIO, quiesce, notify primitives, temperature, host messages, power changes, PCIe/NVMe topology, PCIe link counters, and active cable exceptions.
- Event data structures:
  - log-entry, GPIO, temperature, host-message, power-performance, active-cable, hard-reset, task-set-full, SAS device status, IR operation, IR volume, IR physical disk, IR configuration change list, SAS discovery, SAS broadcast/notify primitives, SAS initiator/table overflow, SAS topology, enclosure, SAS PHY counter, SAS quiesce, host-based discovery PHY, PCIe device status, PCIe enumeration, PCIe topology, and PCIe link counter payloads.
- Firmware transfer and image metadata:
  - `MPI2_FW_DOWNLOAD_REQUEST`, `MPI25_FW_DOWNLOAD_REQUEST`, `MPI2_FW_DOWNLOAD_REPLY`
  - `MPI2_FW_UPLOAD_REQUEST`, `MPI25_FW_UPLOAD_REQUEST`, `MPI2_FW_UPLOAD_REPLY`
  - transaction-context SGEs for upload/download
  - `MPI2_FW_IMAGE_HEADER`, `MPI2_EXT_IMAGE_HEADER`, flash layout data, supported-device image data, init-image footer, and MPI v2.5 encrypted hash data.
- Power and control messages:
  - `MPI2_PWR_MGMT_CONTROL_REQUEST`, `MPI2_PWR_MGMT_CONTROL_REPLY`
  - `MPI26_IOUNIT_CONTROL_REQUEST`, `MPI26_IOUNIT_CONTROL_REPLY`
  - operations for persistent mapping cleanup, SAS link resets, error-log clearing, primitive send, discovery, device removal, mapping lookup, IOC parameters, fast-path enable/disable, NCQ enable/disable, shutdown, persistent connection controls, and NVMe SGL format controls.

## Dependencies And Relationships
This header assumes the core MPI type, version, SGE, and function/status definitions supplied by companion MPI headers such as `mpi2_type.h`, `mpi2.h`, and `mpi2_cnfg.h`. `mpt_sas` uses these layouts when initializing the IOC, discovering controller capabilities, handling asynchronous events, updating firmware/flash regions, and issuing SAS/PCIe control operations.

## Research Notes
The file is versioned as `02.00.30` and explicitly distinguishes MPI v2.0, v2.5, and v2.6 names. Many structures use one-element arrays as variable-length tails; consumers must size buffers from runtime count fields such as `NumElements`, `NumEntries`, `RegionsPerLayout`, `NumberOfLayouts`, or returned image lengths rather than the C `sizeof` alone. Firmware image and flash-region constants are especially relevant to ioctl paths that expose update/upload and diagnostic operations.
