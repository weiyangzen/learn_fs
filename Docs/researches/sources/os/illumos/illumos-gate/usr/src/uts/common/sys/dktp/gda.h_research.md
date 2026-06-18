# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/gda.h

## Scope

Complete file read, 70 lines. This header defines generic disk adapter helpers and logging/error severity constants.

## Public Surface

It defines:

- `GDA_RTYCNT` retry count.
- `GDA_BP_PKT(bp)` mapping from `buf.av_back` to `struct cmpkt *`.
- Kernel prototypes for inquiry string fill, logging, error message formatting, packet preparation, and packet/free cleanup.
- Geometry packing helpers `GDA_GETGEOM_HEAD`, `GDA_GETGEOM_SEC`, and `GDA_SETGEOM`.
- `GDA_KMFLAG(callback)` converting DMA callback sleep policy to `KM_SLEEP` or `KM_NOSLEEP`.
- Error/severity classes `GDA_ALL`, `GDA_UNKNOWN`, `GDA_INFORMATIONAL`, `GDA_RECOVERED`, `GDA_RETRYABLE`, and `GDA_FATAL`.

## Behavior And Integration

Generic disk adapter code uses this header to connect buffers to command packets, log SCSI/DKTP errors, prepare packets with DMA allocation policy, and encode simple head/sector geometry in a single integer.

## Dependencies And Invariants

The kernel section depends on `dev_info_t`, `struct scsi_device`, `struct cmpkt`, `struct buf`, DDI DMA callback constants, and kernel allocation flags.

## Risks

`GDA_BP_PKT` stores packet linkage in `buf.av_back`, which must not conflict with other queue linkage usage. Geometry packing only retains an 8-bit head and 8-bit sector value, with head shifted into bits 16-23.
