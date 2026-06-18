# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/dad_mode.h

This header defines direct-access device mode sense/select constants and selected direct-access mode page layouts.

Key definitions:
- Defines direct-access mode header device-specific bits: write protect and DPO/FUA support.
- Defines medium type constants for direct-access/floppy-like media.
- Defines direct-access mode page codes for error recovery, format, geometry, flexible disk, verify error recovery, caching, media types, notch/partition, and power condition.
- Defines structures:
  - `mode_err_recov` for SCSI-2/3 error recovery parameters
  - `mode_format` for format parameters
  - `mode_geometry` for rigid disk drive geometry
  - `mode_cache_scsi3` for SCSI-3 caching parameters
- Defines page length constants and rotational position locking values.

Dependencies:
- Uses `struct mode_page` from `generic/mode.h`; this header is normally included by that file after `mode_page` is defined.

Impact:
- Target drivers and disk code use these structures to parse and build MODE SENSE/MODE SELECT payloads for direct-access devices.

Cautions:
- The structures use endian-dependent bitfield branches.
- Comments note incompatibilities with older SCSI/CCS variants defined in `impl/mode.h`; callers must distinguish by returned page length.
