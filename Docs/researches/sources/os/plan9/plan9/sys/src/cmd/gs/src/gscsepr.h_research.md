# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.h

## Role

`gscsepr.h` is the client-facing interface for Ghostscript Separation color spaces. It documents that modern Separation handling is mostly implemented as a single-component `DeviceN` color space, with `/All` and `/None` kept as special cases.

## Exposed API

- `gs_cspace_build_Separation(...)` allocates/builds a Separation color space using a separation name, alternate color space, cache size, and memory allocator.
- `gs_build_Separation(...)` initializes the central Separation state inside an already allocated `gs_color_space`.
- `gs_cspace_set_sepr_proc(...)` installs a tint-transform callback with opaque procedure data.
- `gs_cspace_set_sepr_function(...)` installs a `gs_function_t` as the tint transform.
- `gs_cspace_get_sepr_function(...)` retrieves the function object when the transform is function-backed.

## Dependencies

Includes `gscspace.h` for `gs_color_space`, `gs_separation_name`, and memory/color-space types. Forward-declares `gs_function_t` if not already defined.

## Integration Notes

The header is intentionally thin; implementation lives elsewhere in the Ghostscript color-space subsystem. The comments are important because they explain why older multi-entry tint caches are gone and why tint transforms must be executable without interpreter callouts.

## Risks

Callers must pass compatible alternate color spaces and tint transforms. The API exposes mutable `gs_color_space *` setup, so incorrect initialization order can leave compound color-space internals inconsistent.
