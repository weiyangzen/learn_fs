# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.h

Client interface for Ghostscript DeviceN color spaces.

Key contents:
- Includes `gscspace.h`.
- Declares:
  - `gs_build_DeviceN`
  - `gs_cspace_build_DeviceN`
  - `gs_cspace_set_devn_proc`
  - `gs_cspace_set_devn_function`
  - `gs_cspace_get_devn_function`
  - `map_devn_using_function`
  - `gx_serialize_device_n_map`
- Forward-declares `gs_function_t` when needed.

Important implementation notes:
- The header advertises `gs_cspace_set_devn_proc`, but the implementation in `gscdevn.c` is under `#if 0`; clients expecting that symbol may fail unless another implementation exists.
- The comments state that clients own tint-transform function memory management.
- Procedure-name comment notes VMS/old-system symbol-length constraints.
