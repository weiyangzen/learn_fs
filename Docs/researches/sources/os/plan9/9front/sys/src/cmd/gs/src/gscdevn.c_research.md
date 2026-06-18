# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.c

## Role

`gscdevn.c` implements Ghostscript DeviceN color spaces: construction, tint transform mapping, alternate color space fallback, component-name matching against devices, overprint handling, reference counting, and serialization.

This is color/rendering infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_build_DeviceN(...)`
- `gs_cspace_build_DeviceN(...)`
- `alloc_device_n_map(...)`
- `using_alt_color_space(...)`
- `map_devn_using_function(...)`
- `gs_cspace_set_devn_function(...)`
- `gs_cspace_get_devn_function(...)`
- `gx_serialize_device_n_map(...)`

A procedural tint-transform setter, `gs_cspace_set_devn_proc`, exists inside `#if 0` and is not compiled.

## Color Space Type

Defines `gs_color_space_type_DeviceN` with handlers for:

- number of components
- alternate space
- initial color
- color restriction
- concrete color space selection
- concretization
- remapping
- install
- overprint
- reference count adjustment
- serialization
- linearity check via default implementation

## GC Support

- Declares composite descriptor `st_color_space_DeviceN`.
- Uses `private_st_device_n_map()`.
- Enumerates/relocates:
  - `params.device_n.names`
  - `params.device_n.map`
  - `params.device_n.alt_space`

## DeviceN Construction

`gs_build_DeviceN`:

- Validates that alternate color space exists and can be an alternate space.
- Allocates a `gs_device_n_map`.
- Allocates the component name array.
- Sets `names` and `num_components`.

`gs_cspace_build_DeviceN`:

- Allocates a DeviceN color space.
- Calls `gs_build_DeviceN`.
- Intends to initialize the alternate space and return the allocated color space.

## Important Behavior

- Initial DeviceN color sets all components to `1.0`.
- Restriction clamps each component into `[0, 1]`.
- If `use_alt_cspace` is true, concretization runs the tint transform and then concretizes in the alternate color space.
- If `use_alt_cspace` is false, component floats are converted directly to `frac`.
- A one-entry cache exists in `gs_device_n_map`, checking previous tint values before reusing `conc`.
- Additive devices always force alternate color space usage.
- Component-name matching:
  - maps DeviceN component names to device colorants with `get_color_comp_index`
  - accepts `/None`, mapping it to `-1`
  - rejects duplicated component names except `/None`
  - uses the alternate space if any component does not match a device colorant
- Install updates `pgs->color_space->params.device_n.use_alt_cspace` and gives the device a chance to update spot equivalent colors.
- Overprint handling either delegates to alternate space spot-color logic or builds drawn component masks from the color map.
- Serialization supports only function-backed tint transforms; non-function transforms return `gs_error_unregistered`.

## Notable Risks And Suspect Code

- `gs_cspace_build_DeviceN` declares `gs_device_n_params *pcsdevn = 0` and later uses `pcsdevn->alt_space` without assigning it to `&pcspace->params.device_n`. As written, this is a null-pointer-derived address bug.
- `gs_cspace_build_DeviceN` accepts `psnames` but does not copy those names into the allocated `names` array. That conflicts with the function comment saying it allocates and fills the color space.
- `gs_build_DeviceN` also allocates the names array but does not initialize it.
- The one-entry cache is checked in `gx_concretize_DeviceN`, but this file does not visibly update `map->tint`, `map->conc`, or `map->cache_valid` after computing a new mapping.
- Serialization writes raw `gs_separation_name` values, so stability depends on how those names are represented in this Ghostscript build.

## Dependencies

Includes many Ghostscript internals: color spaces, functions, reference counting, matrices, device clients, imager state, overprint, and stream serialization.
