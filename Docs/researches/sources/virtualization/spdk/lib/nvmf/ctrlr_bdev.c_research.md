# File Research: sources/virtualization/spdk/lib/nvmf/ctrlr_bdev.c

## Purpose
Implements the NVMe-oF controller’s bdev-backed namespace command path and bdev-derived Identify data.

## Main Responsibilities
- Determines whether all subsystem namespaces support UNMAP, WRITE ZEROES, or COPY.
- Completes bdev I/O by translating bdev NVMe status into NVMf request completions.
- Builds Identify Namespace and NVM I/O command-set namespace data from bdev properties.
- Parses NVMe read/write parameters and extended command flags into bdev I/O options.
- Implements bdev-backed READ, WRITE, COMPARE, fused COMPARE+WRITE, WRITE ZEROES, FLUSH, DSM/UNMAP, COPY, NVMe passthrough, admin passthrough, ABORT, DIF context creation, and zero-copy start/end.

## Identify Behavior
- Namespace size, capacity, and utilization are taken from bdev block count.
- LBA format is based on bdev descriptor block size and metadata size, or data block size when DIF insert/strip hides metadata.
- DIF/DIX protection fields are mapped from bdev DIF type and metadata placement.
- Preferred write/unmap granularity/alignment and optimal write size are populated from bdev hints, with physical block size fallbacks.
- NGUID, EUI64, reservation capabilities, copy limits, and shared namespace flag are filled from namespace/bdev options.
- NVM-specific Identify data reports PI format details for 16/32/64-bit guard formats.

## I/O Command Behavior
- READ/WRITE/COMPARE validate LBA range and SGL length before issuing vector bdev operations.
- Fused compare/write validates same SLBA/NLB and submits `spdk_bdev_comparev_and_writev_blocks()`.
- WRITE ZEROES validates range, logs WZSL exceedance, rejects deallocate, and submits zeroing.
- FLUSH succeeds immediately if the bdev does not support flush, matching the controller’s volatile-write-cache behavior.
- DSM handles deallocation by splitting NVMe DSM ranges into bdev unmap calls, honoring DMRL/DMRSL-style limits and waiting for all submitted unmaps.
- COPY supports exactly one source range and descriptor format 0, then calls `spdk_bdev_copy_blocks()`.
- NVMe I/O/admin passthrough forwards commands through bdev NVMe passthrough interfaces.

## Resource Handling
- `-ENOMEM` from bdev submission queues the request with `spdk_bdev_queue_io_wait()` and resubmits through the controller command path.
- Request NSID is restored before resubmission because passthrough may have rewritten it.
- Unmap uses a context object to count outstanding range operations and resume after bdev resource waits.
- Abort uses `spdk_bdev_abort()` and updates completion CDW0 when the target command is successfully aborted.
- Zero-copy start preserves the bdev I/O in `req->zcopy_bdev_io` until zcopy end commits or releases it.

## DIF and Zcopy
- DIF context creation derives the initial reference tag from SLBA and enables guard/reference checks according to bdev descriptor settings.
- Zcopy is available only when the bdev supports `SPDK_BDEV_IO_TYPE_ZCOPY`.
- Zcopy start validates range and SGL size, obtains bdev-owned iovecs, and leaves the bdev I/O alive for end-zcopy.

## Storage Relevance
This file is the core data-plane adapter between NVMe-oF protocol commands and SPDK’s block-device abstraction. It is where remote NVMe operations become local bdev I/O.

## Risks / Notes
- Most range validation protects against overflow by checking both end beyond media and wraparound.
- DSM range values are copied from request iovecs via `spdk_iov_xfer`; incorrect host lengths are rejected before use.
- Flush success on non-flush bdevs is a deliberate compatibility choice and does not imply backend persistence semantics.
- Copy and fused operations intentionally expose only limited NVMe functionality based on bdev capabilities.
