# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_targ.h

## Purpose
Defines MPI v2 target-mode wire formats for posting target command buffers, receiving SSP command/task buffers, assisting target data movement, sending target status, returning standard target replies, and aborting target-mode work.

## Main Interfaces
- Command-buffer posting:
  - `MPI2_TARGET_CMD_BUF_POST_BASE_REQUEST`
  - `MPI2_TARGET_CMD_BUF_POST_LIST_REQUEST`
  - `MPI2_TARGET_BUF_POST_BASE_LIST_REPLY`
  - address-space selectors for system memory and IOC memory regions, auto-post-all flag, MSIX index range fields, and IO-index-valid reply flag.
- Target command buffers:
  - `MPI2_TARGET_SSP_CMD_BUFFER`
  - `MPI2_TARGET_SSP_TASK_BUFFER`
  - hashed source SAS address mask/shift, LUN, task attribute, CDB, task management function, managed task tag, and transfer-tag fields.
- Target assist:
  - `MPI2_TARGET_ASSIST_REQUEST` for MPI v2.0
  - `MPI25_TARGET_ASSIST_REQUEST` for MPI v2.5+
  - flags for repost, TLR, retransmit, auto status, direction, bidirectional I/O, multicast, receive-first, and MPI v2.6 escape passthrough.
  - SGL address/type encodings for v2.0 and `DMAFlags` combinations for v2.5 data/cache/interleaved/host-DIF layouts.
  - EEDP/DIF controls for tag increments, guard/app/ref checks, passthrough, strip/insert/replace/regenerate operations, escape modes, and host guard method.
- Status and replies:
  - `MPI2_TARGET_STATUS_SEND_REQUEST`
  - `MPI2_TARGET_SSP_RSP_IU`
  - `MPI2_TARGET_STANDARD_REPLY`
- Aborts:
  - `MPI2_TARGET_MODE_ABORT`
  - `MPI2_TARGET_MODE_ABORT_REPLY`
  - abort types for all command buffers, all I/O, exact I/O, exact request, request plus I/O, initiator device handle, and all commands.

## Dependencies And Relationships
Uses core MPI SGE definitions and scalar typedefs. This header is for SCSI target mode and is separate from initiator I/O, SMP/SATA passthrough, and integrated RAID headers. It shares queue, status, IOC log, VP/VF, and MSIX concepts with the rest of the MPI v2 ABI.

## Research Notes
The file is versioned `02.00.09`. It preserves both MPI v2.0 and v2.5 target-assist formats because DIF/EEDP and SGL representation changed. The SSP response IU is called out as big-endian; little-endian consumers must not treat the field order as ordinary host-native values without conversion.
