# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpe.c

## Role

`gdevpe.c` is the Ghostscript display driver for the Reflection Technology “Private Eye” hardware display.

## Device Model

- Defines `gx_device_pe`, extending `gx_device_common` with a framebuffer address and I/O register base.
- Exposes `gs_pe_device` with fixed geometry `720x280`, 1-bit framebuffer layout, and default framebuffer/register addresses.
- `PEFBADDR` and `PEREGS` environment variables can override hardware addresses.

## Control Flow

- `pe_open()` parses environment overrides and writes the `peinit` register sequence through `outportb()`.
- `pe_close()` restores registers with `pedone` and clears 4000 bytes of framebuffer memory.
- `pe_fill_rectangle()` clips rectangles to the display and sets or clears bits in the framebuffer.
- `pe_copy_mono()` copies 1-bit source bitmaps to the framebuffer with clipping-ish setup, alignment/skew handling, and zero/one color masks.

## Dependencies

Uses low-level hardware I/O (`outportb()`), environment variables, direct memory writes, Ghostscript device procedures, and C runtime parsing/memory functions.

## Risks And Invariants

- This is hardware-specific code that assumes direct access to physical framebuffer memory and VGA-like I/O ports.
- Rectangle loops use `for (; h >= 0; h--)` after computing inclusive bounds; this appears to write one more row than a conventional height loop.
- `pe_copy_mono()` does minimal clipping compared with `pe_fill_rectangle()` and computes destination pointers before fully normalizing negative coordinates.
- Environment parse failures call `exit(1)`, which is unusual for a device open path.
