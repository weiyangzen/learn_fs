# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.h

Header for common Ghostscript DeviceN process-color model support.

Key contents:
- Sets DeviceN limits: `GX_DEVICE_MAX_SEPARATIONS` at 16 and `MAX_DEVICE_PROCESS_COLORS` at 6.
- Defines colorant-name, separation-name, separation-list, separation-map, and `gs_devn_params` structures.
- Declares `DeviceCMYKComponents`.
- Includes `gsequivc.h` for equivalent CMYK spot-color metadata.
- Declares conversion helpers for Gray/RGB/CMYK to DeviceN component arrays.
- Defines automatic spot-color modes: `NO_AUTO_SPOT_COLORS`, `ENABLE_AUTO_SPOT_COLORS`, and `ALLOW_EXTRA_SPOT_COLORS`.
- Declares DeviceN parameter helpers, color-component lookup helpers, `repack_data`, and `bpc_to_depth`.

Research notes:
- The header documents that some routines mutate device color info and DeviceN parameters and do not always restore on error; callers must use the printer wrapper if rollback is needed.
- It is a shared support header for Ghostscript devices with spot-color or DeviceN behavior, not storage/filesystem functionality.
