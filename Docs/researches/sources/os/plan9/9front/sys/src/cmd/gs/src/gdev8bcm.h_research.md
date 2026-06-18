# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.h

## Scope

Header for shared 8-bit dynamic color-map support.

## Key Behavior

- Defines map size `323` and hash spreader `123`.
- Defines compact RGB keying using the top 5 bits of each Ghostscript color channel.
- Defines `gx_8bit_map_entry` and `gx_8bit_color_map`.
- Declares initialization, lookup, fullness test, and add functions.

## Dependencies

Requires `gxdevice.h` color value definitions.

## Risks And Invariants

- Top-5-bit RGB keying trades precision for speed.
- `gx_8bit_no_rgb` is `0xffff`, outside the 15-bit key space.
- The map includes an extra sentinel-sized entry in its array definition.
