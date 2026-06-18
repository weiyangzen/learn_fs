# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacttf.h

Defines small C structures for reading TrueType font directory and naming-table data from Mac font resources.

Types include `TTFontDirComponent`, `TTFontDir`, and `TTFontNamingTable`. The structures model the TrueType table directory and the beginning of the `name` table.

The only tag macro is `TTF_FONT_NAMING_TABLE`, defined as `'name'`. `gdevmacxf.c` uses it to locate the naming table while determining a Mac xfont’s platform encoding.

The file has no functions and no Ghostscript device hooks. It exists solely as a low-level parsing aid for the Classic/Carbon Mac xfont bridge.
