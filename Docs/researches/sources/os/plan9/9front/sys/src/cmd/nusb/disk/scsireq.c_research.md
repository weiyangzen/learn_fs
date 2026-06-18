# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.c

This file is a local copy/adaptation of Plan 9 `scuzz` SCSI request helpers, modified for USB disk support and extra debugging. It builds SCSI command descriptor blocks, dispatches them either through `umsrequest()` for USB transparent SCSI or through an existing raw file descriptor, handles status/sense processing, and exposes higher-level helpers such as inquiry, read, write, seek, mode sense/select, start, and read capacity.

The command builders select 6-, 10-, or 16-byte read/write/seek forms based on block offset, transfer size, and flags. Direct-access devices normally use READ/WRITE(10), while small offsets may use 6-byte commands unless `Frw10` is set. Very large offsets use 16-byte commands. Sequential-device logic supports fixed-block tape-like reads/writes and includes legacy Exabyte-specific behavior.

`SRrequest()` is the central dispatcher. It emits optional debug traces, calls USB or raw transport, records returned status, retries on busy, runs REQUEST SENSE after check-condition status, converts sense data to error strings through `scsierrmsg()`, and returns byte counts on success. The debug helpers format outgoing commands, returned status, partial data bytes, and sense-derived errors.

Device-opening helpers probe inquiry data and initialize device-type-specific state. Direct devices read capacity and set logical block size; sequential devices query block limits and select variable or fixed block modes; WORM/CD-like devices use mode sense for block size. `SRopenraw()` opens a `raw` file in a served disk tree, while `SRopen()` performs readiness and device-type setup.

The implementation preserves broad SCSI support beyond USB disks, but in this group its important role is as the reusable SCSI command library called by `disk.c`.
