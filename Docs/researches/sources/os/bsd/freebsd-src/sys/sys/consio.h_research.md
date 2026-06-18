# File Research: sources/os/bsd/freebsd-src/sys/sys/consio.h

## Purpose
Defines the historical console/vty/video ioctl ABI for keyboard display mode, fonts, mouse cursor control, virtual terminal switching, screenshots, and video mode switching.

## Main Elements
- KD ioctls control text/graphics/pixel modes and raster text setup.
- Screen map, text attribute/color, blanking, saver, bell, history, and cursor shape ioctls.
- Mouse ioctl structs: `mouse_data`, `mouse_mode`, `mouse_event`, `mouse_info`.
- Font ioctls support fixed 8x8/8x14/8x16 fonts and variable fonts (`vfnt_t`).
- Video info/adapter wrappers mirror framebuffer ioctls.
- `scrshot` and `CONS_SCRSHOT` expose screen snapshots.
- `term_info` exposes terminal emulator metadata.
- VT ioctls support open query, process/kernel/auto switching mode, acknowledge release/acquire, activate, wait-active, get active/index, and switch locking.
- Large `SW_*` ioctl set maps legacy text/VGA/VESA mode names to mode IDs.

## Dependencies And Integration
Includes `sys/ioccom.h` and `sys/font.h`; used by syscons/vt drivers and userland console tools.

## Risk Notes
This is a broad legacy ABI. Ioctl numbers and struct layouts must remain stable even where names and behavior are historical or compatibility-only.
