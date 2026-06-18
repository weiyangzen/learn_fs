# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevherc.c

## Role
`gdevherc.c` implements a legacy IBM PC-compatible Hercules Graphics display device using direct frame-buffer access.

## Device Definition
- Defines a `herc` display device at 720x350 pixels, with resolution derived from screen aspect ratio and nominal page height.
- Device procs implement open, close, fill rectangle, copy mono, and copy color; other operations use Ghostscript defaults.

## Hardware Interaction
- Uses DOS BIOS interrupts to save/restore video mode.
- Programs Hercules CRTC registers through I/O ports `0x3b4`, `0x3b8`, `0x3ba`, and `0x3bf`.
- Maps frame-buffer addresses under `regen` (`0xb0000000L`) with Hercules interleaved scanline layout.
- `herc_open` saves text mode, programs graphics registers, selects page 0, and clears the frame buffer.
- `herc_close` restores the saved mode.

## Rendering
- `herc_copy_mono` clips input, handles transparent/explicit zero/one colors, aligns or skews source bits into destination byte positions, and writes masked bytes directly into frame-buffer memory.
- `herc_copy_color` delegates to `herc_copy_mono` with black/white color mapping.
- `herc_fill_rectangle` sets or clears frame-buffer bits for clipped rectangles, handling single-byte and multi-byte spans.

## Risks and Notes
- Deeply tied to 80x86 segmented addressing, DOS BIOS, and Hercules hardware layout.
- No filesystem relevance; it is direct device memory and port I/O code.
