# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfsfnt.h

SFNT/TrueType table structure definitions.

Key points:
- Based on Apple `sfnt.h`, modified to use ISO C exact-size integer types via `stdint_.h`.
- Defines `uint8/int8`, `uint16/int16`, and `uint32/int32` aliases.
- Uses packing pragmas around table structures.
- Defines SFNT offset table and directory entry structures.
- Defines core TrueType table structures:
  - `sfnt_FontHeader`
  - horizontal/vertical metrics headers
  - `sfnt_maxProfileTable`
  - glyph metrics
  - cmap directory/platform/name/mapping structures
  - naming table records
  - device metrics
  - PostScript table info
- Defines glyph flag enums for simple outlines and component glyph packing.
- Defines cmap platform enum.
- Defines reversed-endian four-character table tags such as `head`, `hhea`, `loca`, `maxp`, `cvt `, `prep`, `glyf`, `hmtx`, `vmtx`, `cmap`, `fpgm`, `kern`, `hdmx`, `name`, and `post`.
- Defines `FontTableInfo` and `RAW_TRUE_TYPE_SIZE`.

Dependencies and interactions:
- Used by `ttfinp.c` and `ttfmain.c` for table offsets, field offsets, tags, and glyph flag decoding.

Research relevance:
- Structural map of the SFNT/TrueType binary format used by Ghostscript’s TrueType adapter.
