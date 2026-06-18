# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/smp_frames.h

This large header defines SAS-1.1/SAS-2 SMP frame constants and packed request/response structures for expander management.

Key definitions:
- Defines SMP frame types, function codes, and result codes.
- Defines packed generic request/response frame headers and CRC size/minimum length helpers.
- Defines request/response structures for many SAS-2 SMP functions, including:
  - Report General
  - Report Manufacturer Information
  - Report Self Configuration Status
  - Report Zone Permission Table
  - Report Zone Manager Password
  - Report Broadcast
  - Discover
  - Report PHY Error Log
  - Report PHY SATA
  - Report Route Information
  - Report PHY Event
  - Discover List
  - Report PHY Event List
  - Report Expander Route Table List
  - Configure General
  - Enable/Disable Zoning
  - Zoned Broadcast
  - Zone Lock/Activate/Unlock
  - Configure Zone Manager Password
  - Configure Zone PHY Information
  - Configure Zone Permission Table
  - Configure Route Information
  - PHY Control
  - PHY Test Function
  - Configure PHY Event
- Defines enums and helpers for zone group counts, report types, broadcast types, link rates, device types, routing attributes, PHY event sources, zoning save modes, zoning enable operations, PHY operations, and PHY test functions.
- Defines bitmap helpers for 128/256-zone permission descriptors and route PHY bitmaps.

Dependencies:
- Includes `sys/sysmacros.h` for `DECL_BITFIELD*`.
- Uses `#pragma pack(1)` for frame layouts.

Impact:
- This is the core SMP wire-format catalog for SAS expander discovery, topology inspection, zoning, route management, PHY diagnostics, and PHY control.

Cautions:
- Many structures use trailing one-element arrays for variable-length descriptor lists.
- The macro `SMP_DISCOVER_RESP()` compares against `SMP_FUNCTION_ACCEPTED`, while the enum defines `SMP_RES_FUNCTION_ACCEPTED`; this visible mismatch may depend on another compatibility define elsewhere or may be a latent typo.
- Multi-byte protocol fields are represented as integer types in packed structures, so caller code must still handle SAS/SMP byte ordering correctly.
