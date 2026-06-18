# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm2.h

## Role

`gsiparm2.h` defines Ghostscript ImageType 2 image parameters.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- Opaque `gx_path` forward declaration.
- `gs_image2_t`: common image fields, `DataSource` graphics state pointer, origin/size floats, optional `UnpaintedPath`, and `PixelCopy` flag.
- `private_st_gs_image2()` GC descriptor macro tracks `DataSource` and `UnpaintedPath`.
- `gs_image2_t_init` initializer declaration.

## Important Defaults

The initializer defaults `UnpaintedPath` to `0` and `PixelCopy` to `false`.

## Notable Risks

The type stores a `gs_state *` as `DataSource`; callers and GC descriptors must keep that state reachable and correctly relocated.
