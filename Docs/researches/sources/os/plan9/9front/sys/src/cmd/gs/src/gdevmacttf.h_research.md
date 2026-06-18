# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacttf.h

Defines small TrueType font table structs used by the Mac xfont implementation.

Key contents:
- `TTFontDirComponent`: TrueType table directory entry with tag, checksum, offset, and length.
- `TTFontDir`: TrueType font directory header with version, table count, search metadata, and a flexible first component.
- `TTF_FONT_NAMING_TABLE` tag defined as `'name'`.
- `TTFontNamingTable`: initial fields for reading a TrueType naming table record, including platform, language, name ID, string length, and offset.

Dependencies and notes:
- Uses Mac integer types such as `UInt32` and `UInt16`.
- Only supports the limited table access needed by `mac_get_font_encoding` in `gdevmacxf.c`.
