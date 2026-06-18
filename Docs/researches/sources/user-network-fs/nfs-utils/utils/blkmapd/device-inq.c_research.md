<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-inq.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-inq.c

## Purpose
This file performs SCSI inquiry operations used by `blkmapd` to identify block devices and decide active/passive path state. It converts VPD pages into `struct bl_serial` identities and path states consumed by discovery and deviceinfo matching.

## APIs And Control Flow
`bl_create_scsi_string` allocates a serial object with inline byte storage, and `bl_free_scsi_string` frees it. `bldev_inquire_page` sends an SG_IO INQUIRY command for a standard or EVPD page. `bldev_inquire_pages` first reads a default 255-byte buffer, validates the returned page code, computes the full response length, reallocates up to `MX_ALLOC_LEN`, and retries when needed. `bldev_read_ap_state` reads EMC page `0xc0` and treats low status as passive, otherwise active. `bldev_read_serial` reads VPD page `0x83`, scans designator descriptors, prioritizes NAA/EUI/T10/vendor identifiers, and falls back to the filename when no usable serial is present.

## State, Dependencies, And Integration
There is only static SG timeout state. Dependencies are Linux SCSI SG_IO, SPC VPD page formats, syslog logging macros from `device-discovery.h`, and callers that keep the returned serial until the disk list is released.

## Risks And Test Signals
Risks include signed `char` arithmetic when computing page length, trusting descriptor lengths within one buffer, treating unknown devices as active, and filename fallback causing identity changes across udev naming. Tests should mock SG_IO pages for page `0x83`, page `0xc0`, oversized length rejection, zero-length descriptors, and inquiry failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-inq.c -->
