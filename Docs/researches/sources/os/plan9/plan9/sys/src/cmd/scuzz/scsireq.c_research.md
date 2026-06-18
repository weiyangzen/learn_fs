# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.c

Core SCSI request library for `scuzz`.

Key behavior:
- Builds common SCSI commands: test unit ready, rewind, request sense, format, read block limits, read/write, seek, filemark, space, inquiry, mode select/sense, start/stop, and read capacity.
- Chooses 6-byte versus 10-byte direct-access read/write and seek commands based on offset, transfer count, and `Frw10`.
- Handles sequential devices with fixed or variable block modes.
- Issues requests by writing a CDB to the raw device fd, transferring data, then reading a textual status.
- On check condition, automatically requests sense data and reports `Status_SD`.
- Opens `/dev/sdXX/raw`, performs inquiry, and initializes device-specific flags/block size for direct, sequential, printer, WORM, and changer devices.

Important details:
- Old Exabyte tape quirks are controlled by globals `exabyte` and `force6bytecmds`.
- Sequential reads handle ILI/filemark sense data as short records.
- Direct devices use read capacity to set `lbsize` and may force 10-byte commands for large block addresses.
- USB mass storage can route through `umsrequest()` when `Fusb` is set.

Filesystem relevance:
- Direct: this is the abstraction layer over Plan 9 raw SCSI device files such as `/dev/sdXX/raw`.
