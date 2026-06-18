# File Research: sources/os/plan9/9front/sys/src/cmd/spred/pal.c

`spred/pal.c` implements palette file objects, palette file I/O, palette lookup/reuse, palette drawing, selection, resizing, and color mutation.

Key responsibilities:
- Creates and destroys palettes with `newpal` and `putpal`.
- Reads palette format with `readpal`: first line `pal N`, followed by `N` RGB values, each converted to a 1x1 `Image`.
- Writes palette format with `writepal`, clears dirty state, and reports byte count.
- Finds or loads palettes with `findpal`, using file identity to reuse already-open files.
- Redraws a palette and any sprites using it through `palredraw`.
- Resizes palettes with `palsize`, allocating new color/image entries as needed.
- Draws swatch grids in `paldraw`, including selected-cell border.
- Updates selected color with `palset`, refreshing its backing image and marking dirty.
- Defines palette window behavior through `paltab`, including default zoom, click selection, and zerox state copy.

Important interactions:
- Sprites hold `Pal *` references and use palette images while drawing.
- `findpal` is called by sprite opening and commands to associate sprite palette files.
