# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevice.h

Device-implementor support header layered on `gxdevcli.h`.

- Defines default paper sizes and A4/US Letter selection macros.
- Provides static device-initializer macro families:
  - `std_device_part1_`
  - `std_device_part2_`
  - `std_device_part3_`
  - `std_device_std_body`
  - `std_device_full_body`
  - color and alpha variants
- Declares default optional device procedures:
  - open/close/output/sync
  - color mapping
  - fills/copies/path/image operations
  - RasterOp and strip-copy fallbacks
  - clipping, typed images, compositors, hardware params, text begin
  - high-level color and shading support
- Declares standard color mapping procedures for black-on-white, grayscale, RGB, CMYK, 1-bit CMYK, and 8-bit gray/CMYK.
- Declares forwarding-device procedure implementations for most driver operations.
- Provides implementation utilities:
  - `gx_device_set_procs`
  - `gx_device_fill_in_procs`
  - `gx_device_forward_fill_in_procs`
  - `gx_device_forward_color_procs`
  - `gx_device_copy_color_procs`
  - `gx_device_copy_color_params`
  - `gx_device_copy_params`
- Declares device black/white cache accessors and decache.
- Declares output file parsing/open/close helpers.
- Defines `MIN_CONTONE_LEVELS` and `gx_device_must_halftone`.
- Provides rectangle clipping macros for fill and copy paths.
- Defines input/output media parameter structures and helper functions.

Relationship: `gxdevcli.h` defines the ABI; `gxdevice.h` adds initializer macros, default implementations, and driver utility declarations for implementors.
