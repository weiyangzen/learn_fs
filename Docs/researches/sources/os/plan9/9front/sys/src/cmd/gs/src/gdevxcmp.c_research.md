# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.c

X11 color setup, allocation, and pixel/RGB mapping for the Ghostscript X driver.

Key responsibilities:
- Initializes color management based on X visual class, requested palette, Ghostview color properties, depth, and standard colormap availability.
- Supports standard X colormaps when available, including fast shift/table paths for power-of-two component ranges.
- Allocates synthetic standard colormaps for TrueColor/StaticGray visuals when needed.
- Builds reverse pixel-to-RGB table for small pixel values.
- Allocates dither ramps/cubes for writable colormaps without suitable standard maps.
- Maintains a dynamic color hash table for exact color allocations beyond fixed ramp/cube entries.
- Frees dither, dynamic, reverse-map, and standard-map resources on erase/close.
- `gdev_x_map_rgb_color` maps Ghostscript RGB values to X pixels through foreground/background shortcuts, standard cmap, dither ramp/cube, then dynamic allocation.
- `gdev_x_map_color_rgb` maps X pixels back to Ghostscript RGB via foreground/background, reverse table, standard cmap, dither ramp/cube, or dynamic table.

Notable implementation details:
- Foreground maps to RGB black and background maps to RGB white, preserving Ghostscript device conventions even if X pixels differ.
- `match_mask` may be narrower than `color_mask` when halftoning is not required.
- Dynamic color misses are cached as failed entries too, avoiding repeated allocation attempts.
- The code updates `color_to_rgb` on successful X color allocation/free.

Filesystem relevance:
- None.
