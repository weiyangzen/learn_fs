# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_raid.h

## Purpose
Defines MPI v2 integrated RAID action messages and data structures for creating/deleting volumes, managing physical disks, hot spares, RAID background functions, firmware-update mode, volume indicators, and compatibility checks.

## Main Interfaces
- Action data:
  - `MPI2_RAID_ACTION_DATA`
  - `MPI2_RAID_ACTION_RATE_DATA`
  - `MPI2_RAID_ACTION_START_RAID_FUNCTION`
  - `MPI2_RAID_ACTION_STOP_RAID_FUNCTION`
  - `MPI2_RAID_ACTION_HOT_SPARE`
  - `MPI2_RAID_ACTION_FW_UPDATE_MODE`
- Request/reply:
  - `MPI2_RAID_ACTION_REQUEST`
  - `MPI2_RAID_ACTION_REPLY`
  - `MPI2_RAID_ACTION_REPLY_DATA`
- Action values include indicator query, create/delete volume, enable/disable volumes, physical disk online/offline/fail/hidden, activate/enable failed volume, firmware update mode, write-cache change, volume naming, function-rate changes, hot spare create/delete, system shutdown notification, start/stop RAID function, compatibility check, and product-specific action ranges.
- Volume and operation payloads:
  - `MPI2_RAID_VOLUME_PHYSDISK`
  - `MPI2_RAID_VOLUME_CREATION_STRUCT`
  - `MPI2_RAID_ONLINE_CAPACITY_EXPANSION`
  - `MPI2_RAID_VOL_INDICATOR`
- Compatibility payloads:
  - `MPI2_RAID_COMPATIBILITY_INPUT_STRUCT`
  - `MPI2_RAID_COMPATIBILITY_RESULT_STRUCT`

## Dependencies And Relationships
Depends on shared MPI SGEs and scalar types. It references configuration-page constants from `mpi2_cnfg.h` for RAID volume type and write-cache settings. Event progress and state changes from this command family are mirrored by integrated RAID event structures in `mpi2_ioc.h`.

## Research Notes
The file is versioned `02.00.11`. `MPI2_RAID_VOL_CREATION_NUM_PHYSDISKS` defaults to one but is deliberately build-configurable; callers must account for variable array sizing. The compatibility result encodes protocol, media type, and 4K-sector attributes, which is useful when studying controller-enforced constraints before volume creation or expansion.
