# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.h

Defines shared DeviceN data structures, limits, constants, and utility prototypes.

Core limits are `GX_DEVICE_MAX_SEPARATIONS` at 16 spot colors and `MAX_DEVICE_PROCESS_COLORS` at 6 process colorants. `gs_devn_params_t` stores bits per component, standard process colorant names, `MaxSeparations`, separation-name arrays, and the separation-order map. The header also declares `DeviceCMYKComponents`.

It exposes color-space conversion helpers, automatic spot-color policy constants (`NO_AUTO_SPOT_COLORS`, `ENABLE_AUTO_SPOT_COLORS`, `ALLOW_EXTRA_SPOT_COLORS`), colorant lookup, parameter get/put routines, process/separation name checking, `repack_data`, and `bpc_to_depth`.

Integration is broad: DeviceN-capable devices embed `gs_devn_params` and optionally `equivalent_cmyk_color_params`, then delegate their parameter and colorant-name behavior to these helpers.

Risks: the APIs assume callers maintain consistent `color_info`, separation maps, and allocation lifetime. The comments document that some routines may modify device state without rollback unless callers use the printer wrapper.
