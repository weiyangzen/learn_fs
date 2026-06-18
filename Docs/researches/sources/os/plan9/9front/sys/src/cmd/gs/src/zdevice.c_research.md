# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice.c

Implements core device-related PostScript operators.

Key behavior:
- Provides device copying, `currentdevice`, `.devicename`, `.doneshowpage`, `flushpage`, `.getbitsrect`, `.getdevice`, device/hardware parameter reads, `makewordimagedevice`, `nulldevice`, `.outputpage`, `.putdeviceparams`, and `.setdevice`.
- `.getbitsrect` extracts a rectangle of device bits into a supplied string with alpha/depth options.
- Parameter read/write operators bridge stack parameter lists to `gs_get_device_or_hardware_params` and `gs_putdeviceparams`.
- `.putdeviceparams` reports per-key errors on the operand stack, detects reopening/resizing, and clears current pagedevice state.
- `.setdevice` respects locked safety parameters and returns an erase flag.

Dependencies:
- Uses `gx_device`, get-bits API, stack parameter lists, matrix parsing, image-device creation, and interpreter graphics state.

Research notes:
- Device parameter mutation is stateful and may close/reopen devices; current-device reinstall and pagedevice clearing are key side effects.
