# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_pkt.h

## Purpose
Defines the SCSI packet structure and packet flags, completion reasons, state bits, statistics, and transport return codes.

## Main Interfaces
- Kernel `struct scsi_pkt`: HBA private data, destination address, target private data, completion callback, flags, timeout, status/CDB pointers, residual, state, statistics, reason, allocation metadata, DMA metadata, path instance, and staging pointer.
- Packet flags: queue tags, head/nointr, parallel bus flags, uscsi flags, TLR, MPxIO noqueue/path-instance flags.
- Completion reasons: `CMD_CMPLT`, `CMD_INCOMPLETE`, DMA/transport/reset/abort/timeout/overrun, parallel SCSI failures, `CMD_DEV_GONE`.
- State and statistics bits.
- Transport returns: `TRAN_ACCEPT`, `TRAN_BUSY`, `TRAN_BADPKT`, `TRAN_FATAL_ERROR`.
- Kernel function `scsi_transport`.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. Allocated through `scsi_resource.h` and transported through HBA vectors from `transport.h`.

## Research Notes
The file strongly warns that drivers must not depend on `sizeof (struct scsi_pkt)` and should allocate through SCSA packet allocation interfaces.

## Notable Risks
- Access to newer fields is only valid for correctly allocated packets.
- Misinterpreting `pkt_reason`, `pkt_state`, and `pkt_statistics` can cause bad retry or error reporting behavior.
- `FLAG_PKT_PATH_INSTANCE` must be coordinated with `pkt_path_instance` to avoid retrying failed paths.
