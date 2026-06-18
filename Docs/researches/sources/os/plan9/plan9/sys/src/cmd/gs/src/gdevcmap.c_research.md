# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.c

Special Ghostscript forwarding device that applies PCL5-style color mapping algorithms before passing colors to a target device.

Key responsibilities:
- Defines a forwarding `gx_device_cmap` prototype and GC descriptor.
- Initializes a cmap device over a target device with a selected mapping method.
- Exposes `ColorMappingMethod` through get/put device parameters.
- Adjusts device color model metadata depending on mapping mode.
- Supplies custom color mapping procs for gray, RGB, and CMYK color spaces.
- For non-identity mapping, forces images through the default image renderer so color mapping is applied through the cmap device.

Important behavior:
- Identity mapping forwards the target's color model and color procedures.
- Monochrome mapping converts RGB/CMYK input to gray brightness.
- Snap-to-primaries thresholds gray/RGB/CMY components to full off/on values.
- Color-to-black-over-white maps black to white and other RGB colors to black; CMYK behavior is present but explicitly noted as untested.
- `cmap_begin_typed_image` forwards high-level image handling only for identity mapping; other mappings use `gx_default_begin_typed_image`.

Dependencies:
- Ghostscript device forwarding, color conversion, fraction, image, and parameter APIs.
- Header interface from `gdevcmap.h`.

Notable risks:
- `cmap_put_params` calls `gx_forward_put_params` before reading `ColorMappingMethod`; if target parameter updates fail, behavior depends on `ecode`/`code` handling.
- The CMYK mapping path is marked untested and may not be exercised.
- Non-identity modes intentionally disable target high-level image optimizations.
- Mapping procs call the target's `get_color_mapping_procs` and assume the target implements the relevant callbacks.
