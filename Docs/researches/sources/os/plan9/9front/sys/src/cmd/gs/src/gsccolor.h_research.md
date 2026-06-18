# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccolor.h

## Role

`gsccolor.h` defines Ghostscript client color structures.

This is rendering/color state infrastructure, not filesystem code.

## Main Types

- Forward declaration:
  - `gs_pattern_instance_t`
  - `gs_client_color`
- `gs_paint_color`:
  - `float values[GS_CLIENT_COLOR_MAX_COMPONENTS]`
- `gs_client_color`:
  - `paint`: numeric paint color or uncolored-pattern color
  - `pattern`: optional pattern instance pointer

## Constants

- `GS_CLIENT_COLOR_MAX_COMPONENTS` is 16.
- Comment notes this must be at least 4 and should be at least 6 for hexachrome DeviceN color spaces.

## GC Support

- Declares `extern_st(st_client_color)`.
- Defines `public_st_client_color()` to register one pointer field, `pattern`, with Ghostscript’s structure/GC system.
- `st_client_color_max_ptrs` is 1.

## Dependencies

- Includes `gsstype.h` for `extern_st`.
- Depends on Ghostscript GC macros such as `gs_public_st_ptrs1`.

## Notable Risks

- Fixed-size color component array means callers must respect the 16-component maximum.
