# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.c

## Scope

Configuration table builder identical in content and behavior to `gconf.c`.

## Key Behavior

- Re-includes `gconf.h` under multiple macro definitions to declare configured resources and construct runtime tables.
- Builds compositor, device, halftone, image class, image type, init, and IODevice tables.
- Exposes `gs_find_compositor` and `gs_lib_device_list`.

## Dependencies

Same as `gconf.c`: generated config macros plus Ghostscript graphics/device/resource headers.

## Risks And Invariants

- Must remain synchronized with build-generated resource declarations.
- Runtime resource discovery depends on null-terminated tables and correct generated macro ordering.
