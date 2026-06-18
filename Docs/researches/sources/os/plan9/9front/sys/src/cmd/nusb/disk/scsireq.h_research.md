# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.h

This header defines the SCSI request API and constants shared by the USB disk server and SCSI helper implementation. `ScsiPtr` describes command or data buffers, and `ScsiReq` stores flags, unit/lun identity, block size, current block offset, raw fd, USB LUN pointer, command/data buffers, status, sense data, inquiry data, and tape-read state.

The enums cover software flags (`Fopen`, `Fseqdev`, `Frw10`, `Fusb`, and others), SCSI status codes, internal status values with sense-data/software/bad-argument/read-only meanings, command opcodes for direct, tape, CD/MMC, changer, DVD, and vendor-specific operations, sense-data bit masks, block-address limits, and device types returned by inquiry.

The header also provides big-endian SCSI helper macros (`GETBELONG`, `PUTBELONG`, `GETBE24`, `PUTBE24`) and prototypes for all `SR*` operations, `SRrequest`, raw/open/close helpers, `umsrequest`, `scsidebug`, and `scsierrmsg`.

It intentionally forward-declares `Umsc` so the generic SCSI request object can carry a USB-mass-storage LUN pointer without requiring all USB transport internals.
