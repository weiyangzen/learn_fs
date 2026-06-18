# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.h

## Role

`gscdevn.h` declares the client interface for Ghostscript DeviceN color spaces.

This is rendering/color API surface, not filesystem code.

## Public Functions

- `gs_build_DeviceN(...)`: fill an existing color space.
- `gs_cspace_build_DeviceN(...)`: allocate and fill a DeviceN color space.
- `gs_cspace_set_devn_proc(...)`: set a procedural tint transform.
- `gs_cspace_set_devn_function(...)`: set a tint transform backed by a `gs_function_t`.
- `gs_cspace_get_devn_function(...)`: return the backing function if the tint transform uses one.
- `map_devn_using_function(...)`: adapter that evaluates a `gs_function_t`.
- `gx_serialize_device_n_map(...)`: serialize the DeviceN map.

## Data Ownership Semantics

- Comments state that the client is responsible for memory management of the tint transform Function.
- The color space construction routines allocate or fill the DeviceN color space, but the tint transform is configured separately.

## Dependencies

- Includes `gscspace.h`.
- Forward-declares `gs_function_t` if absent.
- Uses Ghostscript types:
  - `gs_color_space`
  - `gs_separation_name`
  - `gs_memory_t`
  - `gs_imager_state`
  - `gs_device_n_map`
  - `stream`

## Notable Risks

- Header declares `gs_cspace_set_devn_proc`, but the implementation in `gscdevn.c` is disabled under `#if 0`. Callers relying on this symbol may fail to link unless another translation unit provides it.
