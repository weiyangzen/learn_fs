# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdparam.c

## Role

`gsdparam.c` implements default Ghostscript device parameter get/put behavior and helper routines for input/output media dictionaries.

## Get Path

`gs_get_device_or_hw_params` copies read-only prototypes when needed, fills missing device procs, and calls either hardware or normal get-params. `gx_default_get_params` writes standard page-device parameters, non-standard internal parameters, color information, alpha bits, lock-safety state, and optional `HWColorMap`.

Standard parameters include `OutputDevice`, `PageSize`/`.MediaSize`, `ProcessColorModel`, `HWResolution`, `ImagingBBox`, `Margins`, `NumCopies`, `SeparationColorNames`, `Separations`, and `UseCIEColor`.

## Media Helpers

Provides default input/output media structs and functions to begin/write/end `InputAttributes` and `OutputAttributes` dictionaries. Input media can emit page size, media color, media weight, and media type.

## Put Path

`gs_putdeviceparams` calls the device `put_params` proc and reports whether an open device was closed. `gx_default_put_params` validates resolution, size, media size, margins, imaging bbox, copy count, `UseCIEColor`, alpha bits, lock-safety changes, separation-related read-only values, and nominally read-only device/color parameters. It commits the parameter list even on validation errors to surface unknown parameters, then applies changes.

Changing resolution, `HWSize`, or media size closes the device if open and updates dependent geometry. It decaches colors after applying changes.

## Dependencies

Uses `gsparam.h`, `gxdevice.h`, fixed-coordinate limits, color-model helpers, and device geometry functions.

## Risks

Parameter interaction order is intentional: resolution, then size, then media size. Device clients that override parts of this must preserve that order. `.LockSafetyParams` cannot be lowered once set. `PageSize` is accepted as a backward-compatible synonym for `.MediaSize`, with `.MediaSize` taking precedence.
