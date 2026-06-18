# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sff_frames.h

This header defines SFF-8485 GPIO-over-SMP frame formats and register structures.

Key definitions:
- Defines SFF request and response frame headers, distinct from generic SAS SMP frame formats.
- Defines GPIO register type and configuration register index enums.
- Defines packed structures for GPIO configuration registers, receive registers, transmit registers, general-purpose receive/transmit config registers, and register arrays.
- Defines drive error, locate, and activity LED/control enums.
- Defines read GPIO register request/response and write GPIO register request payloads.

Dependencies:
- Includes `sys/sysmacros.h` for `DECL_BITFIELD*`.
- Uses `#pragma pack(1)` for wire/register layouts.

Impact:
- Supports enclosure/backplane GPIO access for SFF-8485 devices, such as drive activity/error/locate signaling.

Cautions:
- The response typedef for `sff_read_gpio_resp` is named `smp_response_frame_t`, which can be confusing because generic SMP frames also define a type with that name in another header.
- GPIO GP register arrays are explicitly little-endian.
