# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.c

## Role

`gscspace.c` implements core color-space construction, copying, reference-count adjustment hooks, base-space accessors, overprint setup, linearity checks, serialization, and GC tracing for Ghostscript color spaces.

## Main Behavior

It defines standard `gs_color_space_type` vectors for `DeviceGray`, `DeviceRGB`, and `DeviceCMYK`. Each vector supplies component counts, initial/restrict paint procedures, concrete/remap procedures, overprint handlers, count-adjustment hooks, serialization, and linearity tests.

The file provides heap allocation and stack initialization for device color spaces:

- `gs_cspace_init`, `gs_cspace_alloc`
- `gs_cspace_init_DeviceGray/RGB/CMYK`
- `gs_cspace_build_DeviceGray/RGB/CMYK`
- `gs_cspace_init_from`, `gs_cspace_assign`, `gs_cspace_release`

Accessors include color-space index, component count, color restriction, and base/alternate color-space lookup.

## Overprint Logic

Generic device/CIE/ICC spaces use `gx_spot_colors_set_overprint`. `DeviceCMYK` has special handling for overprint mode 1: it probes the current device for Cyan/Magenta/Yellow/Black component indexes and verifies that CMYK mapping routes each process component directly. It then intersects drawn process components with nonzero device-color components.

## Linearity

The default linearity check remaps endpoint and midpoint colors to device colors and compares pure device-color components within `smoothness`. Halftones are treated as non-linear and rejected.

## Dependencies

Depends on internal color mapping (`gxcspace.h`, `gxcmap.h`), graphics state (`gzstate.h`, `gxistate.h`), device APIs, overprint compositing, streams, and Ghostscript memory/GC descriptors.

## Risks

Static device color-space prototypes are lazily initialized and not explicitly synchronized. Color-space copy uses each type descriptor’s size and relies on callers to ensure destination storage is large enough. Overprint component probing depends on device color-component names and mapping procedures being correct.
