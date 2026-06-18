# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.h

Fax device declarations and defaults.

Key contents:
- Default fax resolution: 204x196 DPI.
- Defines `gx_device_fax` extension with `AdjustWidth`.
- Defines `FAX_DEVICE_BODY`.
- Declares fax open/get/put params and shared fax print helpers.

Risks / notes:
- Intended to be shared by fax-like devices, including TIFF strip use.
