# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_init.h

MPT MPI SCSI initiator message header.

Key responsibilities:
- Defines SCSI I/O request and reply frames, including target/bus, CDB, LUN, control bits, data length, sense buffer address, SGL, transfer count, sense count, task tag, and response info.
- Defines SCSI I/O message flags for sense buffer width/location.
- Defines LUN addressing masks, data direction flags, task attribute flags, and task-management bits in the SCSI I/O control word.
- Defines SCSI status codes, SCSI state flags, and response-info values.
- Defines SCSI task management request/reply frames and task types for abort, reset, and LUN reset operations.
- Defines simple enclosure processor request/status message support.

Dependencies:
- Uses `sge_io_union_t` and common function/status constants from `mpi.h`.

Notable risks:
- Driver command construction must keep CDB length, sense buffer length/addressing, control direction, and SGL contents consistent.
- Task management values are firmware-facing and affect device reset/abort semantics.
