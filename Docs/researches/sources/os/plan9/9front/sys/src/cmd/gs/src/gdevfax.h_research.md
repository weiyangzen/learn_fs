# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevfax.h

## Role
`gdevfax.h` declares the fax device structure, defaults, device-body macro, and public helper functions implemented in `gdevfax.c`.

## Contents
- Default fax resolution: `X_DPI 204`, `Y_DPI 196`.
- Defines `gx_device_fax`, extending `gx_device_common` and `gx_prn_device_common` with `AdjustWidth`.
- Defines `FAX_DEVICE_BODY`, which creates a 1-bit printer device and initializes `AdjustWidth` to 1.
- Declares fax open/get/put procedures, `gdev_fax_std_procs`, state initialization helpers, strip/page compression helpers.

## Notes
- Header-only API for fax devices and consumers of fax compression.
- No direct I/O behavior in this file.
