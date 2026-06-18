# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_resource.h

## Purpose
Declares SCSA resource allocation and DMA lifecycle functions for SCSI buffers and packets.

## Main Interfaces
- Allocation callback constants: `NULL_FUNC`, `SLEEP_FUNC`.
- Packet init flags: `PKT_CONSISTENT`, `PKT_DMA_PARTIAL`, `PKT_XARQ`, legacy `PKT_CONSISTENT_OLD`.
- Kernel functions: `scsi_alloc_consistent_buf`, `scsi_init_pkt`, `scsi_destroy_pkt`, `scsi_free_consistent_buf`, `scsi_pkt_allocated_correctly`, `scsi_dmaget`, `scsi_dmafree`, `scsi_sync_pkt`, `scsi_pkt2bp`.
- Private `struct scsi_pkt_cache_wrapper` and flags `PCW_NEED_EXT_CDB`, `PCW_NEED_EXT_TGT`, `PCW_NEED_EXT_SCB`, `PCW_BOUND`.
- Defaults for CDB/private/status lengths and obsolete packet/resource allocators.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. Works with `struct scsi_pkt` from `scsi_pkt.h` and HBA packet allocation from `transport.h`.

## Research Notes
The wrapper supports cached packet allocation and stores transfer window and DMA cookie state.

## Notable Risks
- Packet/buffer ownership and DMA cleanup must match allocation path.
- Obsolete interfaces remain for compatibility but should not guide new driver design.
