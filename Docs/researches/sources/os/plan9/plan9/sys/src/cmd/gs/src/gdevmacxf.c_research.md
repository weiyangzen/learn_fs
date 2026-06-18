# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacxf.c

Implements external font (`xfont`) support for the legacy Classic/Carbon MacOS device. It lets Ghostscript render eligible text through local Mac fonts and PICT text opcodes instead of bitmap glyphs.

The file defines MacRoman/ISO/Standard encoding translation tables, the `mac_xfont_procs` procedure record, and the GC structure descriptor `st_mac_xfont`.

`mac_lookup_font` checks `UseExternalFonts`, accepted encodings, font size, and transformation simplicity. It finds a Mac font family/style from the requested name, determines encoding from font resources, measures metrics through QuickDraw font APIs, and returns a `mac_xfont`.

`mac_char_xglyph` maps Ghostscript characters between Standard, ISO Latin-1, and MacRoman encodings. `mac_char_metrics` returns simple metrics from `FMetricRec`. `mac_render_char` emits PICT font-name/font/size/face changes as needed and writes a one-character `LongText` opcode.

`mac_find_font_family` tries full names, dash-normalized names, and basic style suffix extraction. `mac_get_font_encoding` inspects `sfnt` TrueType resources and their naming table platform ID. Optional compatibility wrappers are provided for older FontManager calls when the Carbon macro is disabled.

Limitations: glyph-name lookup is unsupported, transformations are rejected, and some reverse mapping tables are empty.
