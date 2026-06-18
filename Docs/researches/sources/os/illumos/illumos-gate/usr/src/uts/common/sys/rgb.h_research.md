# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rgb.h

## Role

`rgb.h` defines console/display color layout structures, 16-color and 256-entry color-map constants, ANSI/VGA/Sun color translations, and RGB conversion helpers.

## Data Model

`rgb_color_t` describes a color component position and size. `rgb_t` groups red, green, and blue component descriptors and is exported as `rgb_info`.

`text_cmap_t` stores red/green/blue arrays for the 16 base colors. `cmap4_to_24` maps 4-bit text colors to 24-bit components.

## Color Translation

The header defines `pc_colors_t` for standard 16-color VGA ordering and `sun_colors_t` for Sun console ordering. Translation tables include dim/bright mappings and Solaris-to-PC/PC-to-Solaris color arrays.

Functions:
- `rgb_to_color()`
- `rgb_color_map()`

## Research Notes

This is console color-format infrastructure. It bridges bootloader-provided RGB bit layouts, VGA-style colors, and Sun console color ordering.
