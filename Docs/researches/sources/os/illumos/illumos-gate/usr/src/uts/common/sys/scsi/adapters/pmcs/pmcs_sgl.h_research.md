# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_sgl.h

## Purpose
Defines the PMCS external DMA scatter/gather list representation and chunk-management hooks.

## Main Interfaces
- `pmcs_dmasgl_t` is the hardware SGL entry with low/high DMA address, length, and flags.
- `PMCS_DMASGL_EXTENSION` marks an SGL entry as pointing to another SGL array.
- `PMCS_SGL_CHUNKSZ` derives chunk size from `PMCS_SGL_NCHUNKS`.
- `pmcs_dmachunk_t` tracks a linked chunk with virtual SGL array pointer, DMA address, access handle, and DMA handle.
- Prototypes declare DMA load/unload and initialization of newly allocated DMA chunks into the free list.

## Dependencies And Relationships
Consumes sizing from `pmcs_param.h` and command/HBA types from `pmcs.h`. Used by SCSA command DMA mapping before IOMBs are posted.

## Research Notes
The comments note that chunk bookkeeping avoids using reserved firmware fields in SGL entries, preserving compatibility with future firmware revisions.
