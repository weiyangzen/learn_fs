# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/inquiry.h

This implementation-specific inquiry header defines illumos/Sun inquiry sizing and property-name conventions.

Key definitions:
- Defines `SUN_MIN_INQLEN` as the minimum useful inquiry length through the RDF field.
- Defines `SUN_INQSIZE` as `sizeof (struct scsi_inquiry)`.
- Defines inquiry property names:
  - `inquiry-device-type`
  - `inquiry-vendor-id`
  - `inquiry-product-id`
  - `inquiry-revision-id`
  - `inquiry-serial-no`
- Declares kernel helper `scsi_ascii_inquiry_len()`.

Dependencies:
- Included by `generic/inquiry.h`, after `struct scsi_inquiry` is defined.

Impact:
- Provides the property bridge between raw SCSI inquiry data and devinfo/HBA target properties.

Cautions:
- Comments note property values may be richer than the raw fixed-width inquiry fields, especially for SATA revision strings and serial/capacity values obtained outside standard inquiry bytes.
