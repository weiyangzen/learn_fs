# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/antiword.h

Central project header for embedded Antiword. It defines portability constants, platform-specific directories, conversion constants, macros, and cross-module prototypes.

Important contents:
- Requires exactly one of `DEBUG` or `NDEBUG`.
- Establishes path separators, default screen widths, PostScript margins, font names, mapping-file names, and Antiword data directories. For Plan 9, global data directory is `/sys/lib/antiword`.
- Includes `wordconst.h`, `wordtypes.h`, `fail.h`, and `debug.h`.
- Defines generic helpers/macros such as `STREQ`, `ROUND4`, `ROUND128`, `BIT`, `min`, `max`.
- Declares the full Antiword module interface: block/data/depot lists, character translation, drawing/output backends, document parsing, OLE/Word format loaders, image conversion, style/font/list/section handling, XML/PDF/PostScript/text output, and memory wrappers.

Filesystem relevance:
- Coordinates code that reads compound Word/OLE storage streams and maps them into output files.
- Plan 9-specific install paths affect lookup of mapping and font support files.
