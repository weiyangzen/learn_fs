# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.c

Implements DeviceN binary halftoning helpers.

- Provides quotient tables `q0` through `q7` and exported `fc_color_quo` for fast fractional color-level computation.
- `gx_render_device_DeviceN_wts` constructs WTS device colors:
  - sets `gx_dc_type_wts`
  - stores WTS halftone pointer
  - builds `plane_vector` entries by encoding single-component max colors
  - stores fractional component levels
- `gx_render_device_DeviceN` renders DeviceN colors:
  - chooses WTS path if present in the halftone component order
  - computes device-level base values and residual halftone levels
  - returns a pure color when no dithering is required
  - otherwise builds a colored halftone device color and phase
  - reduces one-plane colored halftones when possible
- `gx_devn_reduce_colored_halftone` converts colored halftones with zero or one active varying plane into:
  - a pure color, or
  - a binary halftone
- Handles subtractive devices by inverting both level and color pair for binary halftone reduction.

Role in subsystem: bridges fractional DeviceN color values, device color encoding, and halftone order selection.
