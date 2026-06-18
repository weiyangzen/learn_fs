# File Research: sources/os/bsd/openbsd-src/sbin/atactl/atactl.c

ATA device control utility.

It opens an ATA device with `opendev(..., O_RDWR, OPENDEV_PART, ...)`, dispatches named subcommands, and sends ATA requests through `ATAIOCCOMMAND`. Supported operations include trace dumping, IDENTIFY output, idle/standby/sleep and power status commands, acoustic/APM/read-ahead/write-cache/PUIS feature toggles, ATA security password/unlock/erase/freeze/disable flows, SMART enable/disable/status/autosave/offline/read/readlog, and SMART attribute reading.

The code centralizes ATA command error handling in `ata_command()`, mapping timeout, device-fault, abort, and raw error-register results to fatal diagnostics. IDENTIFY output handles endian conversion and swapped ATA strings, then prints device type, capacity, queue depth, standards, command sets, enabled features, and master password revision.

Security commands use `getpass()` prompts, enforce a 32-byte password limit, optionally confirm new passwords, and send `struct sec_password` sectors for set/unlock/erase/disable. SMART reads validate sector checksums before printing data; log parsing handles directory, summary, comprehensive, and self-test logs, including circular-buffer traversal. The comprehensive log path allocates enough 512-byte sectors for all reported errors before printing each record.

Notable constraints: most subcommands assume direct privileged access to the drive and fail hard on malformed arguments or ioctl errors; SMART attribute names are vendor-style lookup labels and unknown IDs are still displayed with raw values.
