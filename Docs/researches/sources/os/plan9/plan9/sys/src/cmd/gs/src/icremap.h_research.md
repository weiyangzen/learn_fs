# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icremap.h

Defines `int_remap_color_info_t`, used to communicate color remapping procedure and tint values back to the interpreter.

Fields:
- `op_proc_t proc`
- `float tint[GS_CLIENT_COLOR_MAX_COMPONENTS]`

The comment distinguishes pattern remapping, which ignores tints, from DeviceN remapping, which uses them.
