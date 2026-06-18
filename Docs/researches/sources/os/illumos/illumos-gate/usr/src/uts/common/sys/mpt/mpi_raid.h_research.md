# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_raid.h

MPT integrated RAID action and physical-disk passthrough message header.

Key responsibilities:
- Defines RAID action request/reply frames for volume and physical disk management.
- Defines action values for status, create/delete/enable/disable/quiesce volumes, changing settings, online/offline/fail/replace physical disks, and activate/inactivate volume.
- Defines action data flags for synchronization and physical-disk retention/deletion behavior.
- Defines RAID action status values and a volume progress indicator structure.
- Defines SCSI I/O RAID passthrough request/reply frames targeting a physical disk number.

Dependencies:
- Uses `sge_simple_union_t` and `sge_io_union_t` from `mpi.h`.
- Mirrors SCSI I/O control/status patterns from `mpi_init.h`.

Notable risks:
- RAID actions can be destructive; driver control paths must validate action, volume/disk identifiers, and action data.
- Passthrough requests bypass logical volume abstraction and require strict sense/SGL handling.
