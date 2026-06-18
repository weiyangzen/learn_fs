# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi.h

Core LSI MPT MPI v1.x protocol header for illumos MPT storage drivers.

Key responsibilities:
- Defines MPI/header version constants, IOC states, fault codes, PCI doorbell/register offsets, interrupt bits, and message-frame descriptor fields.
- Defines message function IDs for SCSI, IOC, config, FC, RAID, SAS, LAN, inband, diagnostic, reset, and handshake operations.
- Defines scatter/gather element layouts for 32-bit/64-bit simple SGEs, chain SGEs, transaction-context SGEs, and unions used in request frames.
- Provides SGE flag, length, chain-offset, and context-reply manipulation macros.
- Defines common request/reply message headers, common IOC status codes, IOC log-info type masks, and SMP passthrough request/reply structures.

Dependencies:
- Uses fixed-width integer types and is consumed by the sibling MPT headers for config, IOC, initiator, and RAID message formats.

Notable risks:
- This is hardware/firmware ABI. Struct layout, field widths, bit masks, and magic constants must match LSI MPI firmware exactly.
- Several macros mutate fields with read-modify-write semantics; callers must avoid accidental flag/length accumulation.
