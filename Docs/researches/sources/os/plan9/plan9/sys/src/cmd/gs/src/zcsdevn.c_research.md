# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsdevn.c

Implements DeviceN color space setup for LanguageLevel 3.

The sole operator, `.setdevicenspace`, expects a four-element color-space array. The current color space is treated as the alternate space for the new DeviceN space.

The operator validates the component-name array, enforces a nonzero component count and `GS_CLIENT_COLOR_MAX_COMPONENTS`, converts string names to PostScript names when needed, and stores component name indexes into `cs.params.device_n.names`.

It validates the tint transform procedure, resolves it with `ref_function()`, installs it with `gs_cspace_set_devn_function()`, and records interpreter-side references for layer names and tint transform in `istate->colorspace.procs.special.device_n`.

Memory handling explicitly frees `names` and `pmap` on error paths and decrements the map reference after successful `gs_setcolorspace()` because the build path starts it with refcount 1.

Registered through `zcsdevn_op_defs` with `op_def_begin_ll3()`.
