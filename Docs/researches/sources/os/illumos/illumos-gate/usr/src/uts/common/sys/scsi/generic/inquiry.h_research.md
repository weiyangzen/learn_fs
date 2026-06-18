# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/inquiry.h

This header defines standard SCSI INQUIRY data layout, device type constants, qualifier/response-format constants, VPD header/descriptor structures, and power-management capability property bits.

Key definitions:
- `struct scsi_inquiry` models standard inquiry data with separate bitfield layouts for little-to-high and high-to-little systems.
- The structure covers peripheral device type/qualifier, removable bit, version fields, response data format, feature bits, vendor/product/revision IDs, serial/reserved area, SPI-3 byte 56 fields, version descriptors, and padding to 132 bytes.
- Defines peripheral device type constants such as direct, sequential, printer, processor, WORM, optical, changer, array controller, enclosure services, RBC, OSD, ADC, well-known, unknown, and mask values.
- Defines device qualifier values and `DTYPE_NOTPRESENT`.
- Defines response data format constants through SPC-4.
- Defines TPGS failover mode constants.
- Defines VPD page header and identification descriptor structures.
- Defines `pm-capable` property bit masks for SCSI power-management/logging capabilities.
- Includes implementation-specific inquiry additions.

Dependencies:
- Includes `impl/inquiry.h` at the end.

Impact:
- This is the canonical SCSA structure for standard inquiry data and device identification.
- It feeds target-driver attach decisions, diagnostic naming, property generation, and multipath/device identity logic.

Cautions:
- The file contains many deprecated/obsolete SPC fields that are preserved for ABI/source compatibility.
- Driver code must mask `inq_dtype` with `DTYPE_MASK` when checking device type because qualifier bits share the byte.
