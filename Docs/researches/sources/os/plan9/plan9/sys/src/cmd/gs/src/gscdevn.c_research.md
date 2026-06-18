# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.c

Implements Ghostscript DeviceN color space behavior.

Key contents:
- Includes Ghostscript memory, color-space, function, graphics-state, device, overprint, and stream headers.
- Defines GC descriptors for `gs_color_space_DeviceN` and `gs_device_n_map`.
- Defines `gs_color_space_type_DeviceN`, wiring DeviceN callbacks:
  - component count
  - alternate space access
  - color initialization/restriction
  - concrete-space selection
  - concretization
  - concrete color remapping
  - install
  - overprint setup
  - reference-count adjustment
  - serialization
- Public construction/helpers:
  - `gs_build_DeviceN`
  - `gs_cspace_build_DeviceN`
  - `alloc_device_n_map`
  - `using_alt_color_space`
  - `map_devn_using_function`
  - `gs_cspace_set_devn_function`
  - `gs_cspace_get_devn_function`
  - `gx_serialize_device_n_map`
- Disabled block contains an unused direct-procedure tint-transform setter, `gs_cspace_set_devn_proc`, not supported by serialization.

Behavior:
- `gs_build_DeviceN` validates that the alternate color space can be used as an alternate space, allocates the DeviceN map, allocates component-name storage, and stores component count.
- `gs_cspace_set_devn_function` validates function arity: input count must match DeviceN components, output count must match alternate-space component count.
- `gx_init_DeviceN` initializes all DeviceN component values to `1.0`.
- `gx_restrict_DeviceN` clamps components into `[0, 1]`.
- `gx_concrete_space_DeviceN` returns the alternate concrete space when `use_alt_cspace` is active; otherwise DeviceN is treated as concrete.
- `gx_concretize_DeviceN` either:
  - runs the tint transform and concretizes through the alternate color space, with a one-entry cache check, or
  - maps DeviceN component floats directly to fractional values when not using alternate space.
- `check_DeviceN_component_names` compares DeviceN component names with device colorant names, handles `/None`, rejects duplicated non-`None` names, and decides whether the alternate color space must be used.
- Additive devices always use the alternate color space.
- `gx_install_DeviceN` installs the color space and lets the device update equivalent spot colors.
- `gx_set_overprint_DeviceN` either delegates overprint to the alternate color space or computes drawn DeviceN components.
- Serialization only supports maps whose tint transform is `map_devn_using_function`; arbitrary procedure transforms return `gs_error_unregistered`.

Important implementation notes:
- DeviceN behavior is tightly coupled to `gs_devicen_color_map` in the graphics state and to device colorant-name lookup.
- As written in this snapshot, `gs_cspace_build_DeviceN` initializes `gs_device_n_params *pcsdevn = 0` and then calls `gs_cspace_init_from((gs_color_space *)&pcsdevn->alt_space, palt_cspace)` without assigning `pcsdevn = &pcspace->params.device_n`; this appears to be a null-pointer bug in the checked-in source.
- The comment in `gs_build_DeviceN` repeats “color names list” for both map and names allocation; the first is actually map allocation.
