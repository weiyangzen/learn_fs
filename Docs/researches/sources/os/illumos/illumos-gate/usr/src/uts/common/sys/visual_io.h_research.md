# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/visual_io.h

## Role

`visual_io.h` defines the Solaris VISUAL framebuffer ioctl interface for device identification, color maps, hardware cursors, software console initialization, console drawing, polled I/O, and framebuffer/terminal-emulator integration.

## Key Interfaces

Public user-facing pieces include:
- `VIS_GETIDENTIFIER` and `struct vis_identifier`.
- cursor-position, cursor-colormap, and cursor-shape structures.
- `VIS_SETCURSOR`, `VIS_GETCURSOR`, `VIS_MOVECURSOR`, and `VIS_GETCURSORPOS`.
- `VIS_GETCMAP` and `VIS_PUTCMAP` with `struct vis_cmap`.

Kernel/standalone console pieces include:
- `VIS_DEVINIT`, `VIS_DEVFINI`, `VIS_CONSCURSOR`, `VIS_CONSDISPLAY`, `VIS_CONSCOPY`, and `VIS_CONSCLEAR`.
- screen coordinate typedefs.
- `color_t`, a union covering mono, 4-bit, 8-bit, 16-bit, 24-bit, and 32-bit pixel encodings.
- `struct vis_consdisplay`, `vis_conscopy`, `vis_conscursor`, and `vis_consclear`.
- `struct vis_polledio`, providing display/copy/cursor callbacks usable in polled contexts.
- `struct vis_devinit`, exchanged between terminal emulator and framebuffer driver.
- `struct visual_ops`, the framebuffer operation table.

## Integration Points

The comments explain the console layering model: framebuffer drivers that support software console operation must expose low-level operations usable by kmdb or other polled contexts where normal DDI services, locks, and copy routines may not be available.

## Research Notes

This header is an ABI and driver-contract file. The most important risks are pointer ownership/copyin behavior for user ioctls and the strict context restrictions for polled console routines.
