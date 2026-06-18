# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.c

## Role

`gscsepr.c` implements Ghostscript Separation color spaces: construction, tint-transform function binding, device colorant matching, alternate color-space fallback, concretization/remapping, overprint behavior, and serialization.

This is color-management/color-space infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_color_space_type_Separation`
- `gs_build_Separation`
- `gs_cspace_build_Separation`
- `gs_cspace_set_sepr_function`
- `gs_cspace_get_sepr_function`

The disabled `gs_cspace_set_sepr_proc` exists under `#if 0`.

## Core Behavior

A Separation color space has one tint component, a separation name, an alternate color space, and a `gs_device_n_map` tint transform.

Construction validates that the alternate color space can be an alternate space, allocates the DeviceN-style map, stores the separation name, and initializes the alternate space copy.

Installation calls `check_Separation_component_name`, stores whether alternate color space should be used, optionally installs the alternate color space, and lets the device update spot equivalent colors.

Component-name checking:

- treats `SEP_NONE` and `SEP_ALL` as special and avoids alternate space
- forces alternate space on additive devices
- converts the separation name to a byte string using the color-name callback
- asks the device for a colorant index
- maps absent or out-of-order colorants to alternate-space use or `-1`

Concretization either applies the tint transform and concretizes in the alternate color space or returns the tint as a unit frac for direct separation output.

Overprint retains spot components when overprint is enabled and the separation is not `/All`, with special handling for `/None`.

Serialization writes the separation name, alternate color space, DeviceN map, and separation type; `use_alt_cspace` is intentionally not serialized as intrinsic color-space state.

## Dependencies

Uses function objects, DeviceN map helpers from `gscdevn.h`/`gxcdevn.h`, color-space internals, device colorant callbacks, overprint state, and stream serialization.

## Notable Risks

- `gs_build_Separation` allocates the map but does not itself initialize the alternate space or separation name; callers must complete setup.
- `gx_concretize_Separation` checks a one-element map cache and copies cached concrete values, but the visible path does not update that cache after a miss.
- The raw procedure-based tint transform setter is disabled because serialization only supports function-backed maps.
- Name-string storage returned by `get_colorname_string` is assumed valid for immediate device comparison.
