# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpcfb.h

## Purpose

`gdevpcfb.h` defines the shared types, constants, port-register macros, and platform abstractions for IBM PC EGA/VGA framebuffer devices implemented in `gdevpcfb.c`.

## Contents

It declares EGA device procs (`ega_open`, `ega_close`, `ega_fill_rectangle`, `ega_tile_rectangle`, `ega_copy_mono`, `ega_copy_color`, `ega_get_bits`) and BIOS state helpers. `pcfb_bios_state` records display mode, text page, cursor mode, font, text attribute, and border color for restoration.

`gx_device_ega` extends `gx_device_common` with framebuffer raster, segmented-address multipliers, and video mode. The `ega_device` macro builds device descriptors with page-like DPI derived from screen height and aspect ratio.

The header defines EGA/VGA sequencer and graphics-controller ports/registers, helper macros such as `set_s_map`, `set_g_const`, `set_g_mask`, and `mk_fb_ptr`, plus the `regen` base segment. For Unix-like builds it provides inline `outb`/`outw` assembly for GCC or external declarations, and redefines `mk_fb_ptr` around a flat `fb_addr`. For MS-DOS it uses segmented pointers and `dos_.h`.

## Dependencies and Integration

The header bridges Ghostscript device code with platform-specific port/framebuffer access. It also defines `fb_ptr`, `volatile_fb_ptr`, `PAGE_HEIGHT_INCHES`, and `byte_discard` to force hardware read side effects.

## Filesystem Relevance

No filesystem functionality exists in this header.

## Risks and Notes

The macros encode direct hardware I/O and memory-addressing assumptions. They require privileged port access on Unix-like systems and segmented-address compatibility on DOS. `byte_discard` exists specifically to prevent compilers from removing reads needed to load VGA latches.
