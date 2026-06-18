# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_tool.h

## Purpose
Defines MPI v2 diagnostic and toolbox command layouts used for controller maintenance: flash/NVRAM cleanup, memory move, diagnostic data upload, ISTWI access, beacon control, diagnostic CLI, text display, diagnostic buffer posting, and diagnostic buffer release.

## Main Interfaces
- Toolbox selectors:
  - clean, memory move, diagnostic data upload, ISTWI read/write, beacon, diagnostic CLI, and text display tool IDs.
- Common toolbox reply:
  - `MPI2_TOOLBOX_REPLY`
- Clean and memory tools:
  - `MPI2_TOOLBOX_CLEAN_REQUEST`
  - `MPI2_TOOLBOX_MEM_MOVE_REQUEST`
  - clean flags for boot services, manufacturing/persistent pages, current/backup firmware, MegaRAID, initialization, SBR/SBR backup, HII, controller, IMR firmware, MR NVDATA, all-but-MPB, entire flash, flash, SEEPROM, and NVSRAM.
- Diagnostic upload:
  - `MPI2_TOOLBOX_DIAG_DATA_UPLOAD_REQUEST`
  - `MPI2_DIAG_DATA_UPLOAD_HEADER`
- ISTWI:
  - `MPI2_TOOLBOX_ISTWI_READ_WRITE_REQUEST`
  - `MPI2_TOOLBOX_ISTWI_REPLY`
  - actions for read, write, sequence, reserve bus, release bus, and reset; flags for auto reserve/release and page address.
- Beacon, CLI, and text display:
  - `MPI2_TOOLBOX_BEACON_REQUEST`
  - `MPI2_TOOLBOX_DIAGNOSTIC_CLI_REQUEST`
  - `MPI25_TOOLBOX_DIAGNOSTIC_CLI_REQUEST`
  - `MPI2_TOOLBOX_DIAGNOSTIC_CLI_REPLY`
  - `MPI2_TOOLBOX_TEXT_DISPLAY_REQUEST`
- Diagnostic buffers:
  - `MPI2_DIAG_BUFFER_POST_REQUEST`
  - `MPI2_DIAG_BUFFER_POST_REPLY`
  - `MPI2_DIAG_RELEASE_REQUEST`
  - `MPI2_DIAG_RELEASE_REPLY`
  - buffer types for trace, snapshot, and extended; extended utilization type; release-on-full and immediate-release flags.

## Dependencies And Relationships
Uses MPI SGE unions and scalar typedefs. `mptsas_ioctl.h` exposes higher-level userland diagnostic actions that correspond to these firmware buffer operations. Firmware image-region constants in `mpi2_ioc.h` align with many of the clean-tool flags.

## Research Notes
The file is versioned `02.00.14`. Diagnostic CLI has separate MPI v2.0 and v2.5 request layouts because the SGE format changed. Diagnostic buffer post includes 23 product-specific words, so callers should preserve/round-trip vendor data rather than assuming illumos owns those fields.
