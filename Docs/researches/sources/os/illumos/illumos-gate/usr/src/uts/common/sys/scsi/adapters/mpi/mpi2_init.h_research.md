# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_init.h

## Purpose
Defines MPI v2 SCSI initiator-mode request and reply message layouts for SCSI I/O, SCSI task management, and SCSI enclosure processor operations. These structures are the adapter firmware ABI used by illumos MPI SCSI drivers to submit CDBs, describe data movement and protection metadata, receive completion status, issue task-management functions, and manipulate/report enclosure slot state.

## Main Interfaces
- SCSI I/O CDB and request payloads:
  - `MPI2_SCSI_IO_CDB_EEDP32`
  - `MPI2_SCSI_IO_CDB_UNION`
  - `MPI2_SCSI_IO_REQUEST`
  - `MPI25_SCSI_IO_CDB_UNION`
  - `MPI25_SCSI_IO_REQUEST`
- SCSI I/O request constants:
  - `MsgFlags` sense-buffer address-space selectors
  - MPI v2.0 `SGLFlags` address/type selectors and SGL offset shifts
  - MPI v2.5 `DMAFlags` patterns for data/cache-DIF/interleaved/host-DIF placement
  - I/O path, large CDB, bidirectional, multicast, command-determines-direction, escape passthrough, and CDB length flags
  - EEDP flags for reference/application/guard checking, pass-through, strip/remove/insert/replace/check-regenerate operations, escape modes, and host guard methods
  - SCSI control bits for additional CDB length, data direction, task/command priority, task attribute, and TLR
- SCSI I/O completion:
  - `MPI2_SCSI_IO_REPLY`
  - SCSI status constants matching SAM-4 values
  - SCSI state flags for response info, terminated, no status, autosense failed, and autosense valid
  - response-info masks and EEDP observed value validity flags
- SCSI task management:
  - `MPI2_SCSI_TASK_MANAGE_REQUEST`
  - `MPI2_SCSI_TASK_MANAGE_REPLY`
  - task types for abort task, abort task set, target reset, logical unit reset, clear task set, query task, clear ACA, query task set, and query asynchronous event
  - target-reset message flags for SAS link/hard reset and MPI v2.6 PCIe reset forms
  - task-management response codes and response-info masks
- SCSI Enclosure Processor messages:
  - `MPI2_SEP_REQUEST`
  - `MPI2_SEP_REPLY`
  - actions for read/write status
  - addressing flags for devhandle versus enclosure/slot
  - slot status request/reply bits for device off, request/remove-ready, identify, rebuild stopped, hot spare, unconfigured, predicted fault, critical/failed array membership, rebuilding, faulty, and no-error state

## Dependencies And Relationships
This header depends on core MPI definitions from `mpi2.h`, including base integer typedefs, pointer aliases, LUN field constants, MPI/IEEE SGE unions, and common IOC status/log-info handling. It is functionally adjacent to `mpi2_cnfg.h`: configuration pages identify devices, handles, enclosures, and transport capabilities, while these initiator messages perform I/O and task/enclosure operations against those handles.

## Research Notes
The header identifies itself as `mpi2_init.h` version `02.00.21`, with history through January 21, 2016. It preserves separate MPI v2.0 and MPI v2.5/2.6 SCSI I/O request layouts. The v2.5/2.6 form replaces v2.0 `SGLFlags` with `DMAFlags`, changes the EEDP block-size field width, uses IEEE SGE forms in the CDB union, and adds fast-path/escape passthrough/PCIe-oriented flags. The SCSI I/O reply is shared for MPI v2.0 and v2.5+, with later EEDP observed fields marked as reserved for older controllers.

The optional vendor-unique request region is controlled by preprocessor symbols and is normally left undefined. SCSI LUN encoding is intentionally not redefined here; callers are directed to common `MPI2_LUN_` definitions in `mpi2.h`.

## Notable Risks
- These request/reply layouts are firmware ABI. Offsets, union sizes, SGL placement, and reserved fields must remain exact.
- MPI v2.0 and v2.5/2.6 SCSI I/O requests are similar but not interchangeable; using the wrong structure changes interpretation of data movement, EEDP, and SGE fields.
- EEDP/DIF flags and DMAFlags are dense bitfields. Incorrect combinations can silently alter protection-information checking, insertion/removal, or data/DIF placement.
- SCSI task-management messages can reset links, targets, or logical units. Misusing task type or reset flags can disrupt unrelated I/O.
- SEP slot-status bits are split into request and reply meanings. Code must distinguish requested state changes from reported enclosure state.
