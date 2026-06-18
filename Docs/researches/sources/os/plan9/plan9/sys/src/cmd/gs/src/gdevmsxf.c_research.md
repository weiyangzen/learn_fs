# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmsxf.c

Microsoft Windows external-font implementation for Ghostscript.

- Exposes `win_get_xfont_procs`, returning lookup, glyph mapping, metrics, render, and release callbacks.
- Defines `win_xfont`, holding Ghostscript xfont state, Windows `LOGFONT`, `TEXTMETRIC`, `HFONT`, owning Windows device, y inversion, and y offset.
- Contains Standard/Symbol/ISO-to-OEM mapping tables for Windows character sets.
- Maps common PostScript font families to Windows face names: Courier, Helvetica/Arial/Helv, and Times/Times New Roman/Tms Rmn.
- `win_lookup_font` accepts only simple non-skewed, uniform-scale matrices and small sizes, builds `LOGFONT`, matches logical fonts against Windows faces, records metrics, and allocates a `win_xfont`.
- `win_char_xglyph` maps Ghostscript characters to Windows glyph codes based on encoding and selected font charset.
- `win_char_metrics` selects the font into a desktop DC and returns width plus a bbox derived from ascent/descent and y inversion.
- `win_render_char` renders required glyphs into a temporary 1-bit Windows bitmap, extracts bits, and copies them to the target device with `copy_mono`; optional direct-window rendering is disabled.
- `win_release` deletes the Windows font and frees the Ghostscript xfont object.
- Risk notes: uses desktop DCs because the driver has no owned window; rendering uses legacy `GetBitmapBits` and temporary GDI objects that must be carefully released.
