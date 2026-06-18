# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmsxf.c

## Role

Windows external-font (`xfont`) implementation for Ghostscript.

## Main Interfaces

- `win_get_xfont_procs` returns the Windows xfont procedure table.
- `win_lookup_font` maps eligible PostScript font requests to Windows logical fonts.
- `win_char_xglyph` maps Ghostscript character/encoding inputs to Windows glyph codes.
- `win_char_metrics` obtains glyph metrics from GDI.
- `win_render_char` renders a glyph into a 1-bit Windows bitmap and copies it into a Ghostscript device.
- `win_release` frees the Windows font resource.

## Data Tables

- `gs_map_symbol_to_oem` and `gs_map_iso_to_oem` map PostScript/Symbol/ISO encodings to Windows OEM characters.
- `font_names` maps common PostScript font families to Windows faces such as Courier New, Arial, Helv, Times New Roman, and Tms Rmn.

## Main Constraints

`win_lookup_font` handles only simple unrotated, uniformly scaled matrices; it rejects skew, negative x scale, and sizes outside a narrow range. It also only handles simple character-code mapping, not glyph-name lookup.

## Rendering Path

For required rendering, it creates a compatible bitmap, draws text with `TextOut`, reads bitmap bits with `GetBitmapBits`, then uses the target device’s `copy_mono` procedure. Y inversion is handled by copying scan lines in reverse order.

## Risks and Edge Cases

- Direct rendering to owned windows is disabled under `NOTUSED`.
- Character-set support is limited to ANSI and OEM paths.
- Font face matching uses prefix comparisons and hard-coded mappings.
