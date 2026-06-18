# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.c

## Purpose
Implements Ghostscript Separation color spaces.

## Key Behavior
- Defines the Separation color-space type descriptor.
- Enumerates/relocates alternate color spaces and DeviceN maps for GC.
- Returns the alternate space only when `use_alt_cspace` is active.
- Installs Separation spaces by checking the separation component name against the current device and deciding whether to use the alternate space.
- Updates spot-equivalent colors on the device after installation.
- Sets overprint parameters for spot separations, `All`, and `None`.
- Adjusts reference counts for the tint map and alternate color space.
- Builds Separation spaces over an alternate color space.
- Sets or retrieves tint-transform Functions.
- Initializes Separation color to tint `1.0`.
- Remaps `None` separations to null color.
- Concretizes either through the alternate color space and tint transform or directly to a separation tint.
- Remaps concrete Separation colors directly for devices that support them or through the alternate space otherwise.
- Serializes separation name, alternate space, DeviceN map, and separation type.

## Important Details
- Devices with additive polarity always use the alternate color space for Separations.
- `check_Separation_component_name` populates `pgs->color_component_map` and maps named colorants to device component indexes.
- A colorant found in `SeparationNames` but absent from `SeparationOrder` maps to `-1`.
- `SEP_NONE` paints a null device color.
- The old multi-element separation cache path is removed; comments preserve design notes.

## Dependencies
Uses DeviceN map helpers, Function tint transforms, color-space internals, device colorant lookup, overprint state, device client procs, graphics-state internals, and stream serialization.

## Research Notes
Separation behavior is device-dependent: the same color space can become concrete spot output on a subtractive colorant-aware device or fall back to alternate-space rendering on additive or unsupported devices.
