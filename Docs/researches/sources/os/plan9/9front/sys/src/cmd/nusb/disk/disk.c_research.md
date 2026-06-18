# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/disk.c

This file is the USB mass-storage 9P file server. It supports SCSI transparent command devices over USB bulk-only transport and exposes each logical unit as a small disk tree with `ctl`, `raw`, `data`, and user-defined partition files.

Partition management is adapted from Plan 9 disk/partfs. `addpart`, `delpart`, `lookpart`, `freepart`, `fixlength`, and `makeparts` maintain per-LUN `Part` entries in block units. The `ctl` file reports inquiry, USB device path, LUN number, geometry, and extra partitions; writes accept `part name start end` and `delpart name`.

USB mass-storage setup starts by finding bulk endpoints for either bulk-only (`Protobulk`) or UAS protocol ids, issuing class-specific reset and Get Max LUN requests, and probing each LUN with SCSI inquiry and capacity reads. Capacity supports both READ CAPACITY(10) and READ CAPACITY(16) when the 10-byte response reports `0xffffffff`.

`umsrequest()` is the transport bridge used by `scsireq.c`: it builds a command block wrapper, writes it to the OUT endpoint, transfers optional data, reads and validates a command status wrapper, maps CSW status to SCSI status, handles residue quirks, and reports hard errors for phase failures.

The 9P implementation maps root entries to LUN directories and LUN entries to partition/control files. Normal `data` and partition I/O uses `setup()` to align arbitrary byte offsets/counts to logical blocks, using an intermediary block buffer for partial-block reads/writes. `raw` implements a three-phase command/data/status interface for direct SCSI command passthrough.

The main routine parses debug flags, opens and configures the USB device, performs mode-switch exits for known fake-storage modem/NIC devices, applies a SanDisk residue quirk, initializes LUNs, names them `sdU...`, and posts the service under `/srv/usb`.
