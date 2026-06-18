# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdcolor.h

## Role

`gsdcolor.h` defines the device-color representation used by Ghostscript drivers and painting internals.

## Data Model

A `gx_device_color` has a type tag, base color union, phase, optional preserved client color, and optional Pattern mask. It represents:

- unset/null colors
- pure device colors
- binary halftones
- colored halftones
- Well-Tempered Screening levels
- colored Pattern tiles
- Pattern masks

The file separates read-only driver helpers from mutation macros, then exposes lower-level internals because many callers need inline access for performance.

## Key Helpers

Macros detect and extract pure, binary halftone, and colored halftone colors; set null/pure/binary/tile/pattern states; set halftone phase; and mark non-client special colors. It declares `gx_device_color_equal` and `gx_complete_halftone`.

## Saved Colors

`gx_device_color_saved` is a compact non-owning representation used by command-list/vector devices to avoid resending redundant color state. It intentionally avoids storing halftone pointers because device-color references to halftones are not reference-counted.

## Dependencies

Includes client color, bitmap, halftone tile, color index, arithmetic, and WTS headers.

## Risks

Many macros mutate multiple fields without statement wrappers, so call-site syntax matters. Device colors may contain non-reference-counted pointers to halftones/tiles; saved colors deliberately avoid some pointers, making them unsuitable for fully restoring Pattern state.
