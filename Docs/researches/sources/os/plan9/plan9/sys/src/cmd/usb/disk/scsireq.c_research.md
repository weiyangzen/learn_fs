# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.c

Read fully: 987 lines, 19672 bytes. SHA-256 prefix: `30cd71259cab8c53`.

This file is a local copy/adaptation of Plan 9 `scuzz` SCSI request helpers, with extra debug support and USB transport support. It builds SCSI command descriptor blocks, routes requests through raw scuzz devices or `umsrequest()`, handles sense data, and provides open/read/write/seek/capacity helpers.

Command helpers include TEST UNIT READY, REWIND, REQUEST SENSE, FORMAT, READ BLOCK LIMITS, READ/WRITE(6/10), SEEK(6/10), FILEMARK, SPACE, INQUIRY, MODE SELECT/SENSE(6/10), START STOP, READ CAPACITY(10), and READ CAPACITY(16). Direct-access requests use 10-byte commands when offsets/counts exceed 6-byte limits or flags request them.

`SRrequest()` dumps debug traces, calls the selected transport, maps status, requests sense on check condition, retries busy devices, and sets `werrstr()` from `scsierrmsg()`. Open helpers configure direct, sequential, WORM/CD, printer, and changer device flags and block sizes.

Integration: used by `usb/disk/disk.c`; header notes it is also included by cdfs/scuzz contexts. For USB, `Fusb` and `umsc` route requests to the bulk-only transport.

Risk notes: comments acknowledge incomplete behavior. `exabyte` and `force6bytecmds` global quirks affect command selection and error handling. Sequential/tape short-read logic is preserved even though USB disk primarily uses direct-access devices.
