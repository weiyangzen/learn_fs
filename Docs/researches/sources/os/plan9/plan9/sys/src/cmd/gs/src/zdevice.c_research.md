# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice.c

Implements core device-related PostScript operators.

Major operators include `.copydevice2`, `currentdevice`, `.devicename`, `.doneshowpage`, `flushpage`, `.getbitsrect`, `.getdevice`, `.getdeviceparams`, `.gethardwareparams`, `makewordimagedevice`, `nulldevice`, `.outputpage`, `.putdeviceparams`, and `.setdevice`.

`zgetbitsrect()` is the main raster extraction bridge. It validates device, rectangle, alpha placement, optional standard component depth, target string size, and calls the device `get_bits_rectangle` procedure.

`zget_device_params()` writes device or hardware parameters onto the operand stack using `stack_param_list_write()` and inserts a mark before returned key/value pairs.

`zputdeviceparams()` reads key/value parameter pairs from the operand stack, applies them to a device, reports per-key failures, detects size/open-state changes, may reinstall the current device, and clears the current page device.

`zsetdevice()` respects `LockSafetyParams`, preventing switching to a different device when safety parameters are locked. `nulldevice`, `.setdevice`, and `.putdeviceparams` clear `istate->pagedevice`.

Registered in `zdevice_op_defs`.
