# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.h

## Role

`gscpixel.h` declares the DevicePixel color-space initialization API.

This is rendering/device color API infrastructure, not filesystem code.

## Public API

- `gs_cspace_init_DevicePixel(gs_memory_t *mem, gs_color_space *pcs, int depth)`

## Dependencies

Requires `gscspace.h` context for `gs_color_space` and memory types.

## Notable Risks

Header only; accepted depth validation and raw-pixel limitations are in `gscpixel.c`.
