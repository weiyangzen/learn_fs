# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordtypes.h

Shared type definitions for Antiword’s parser and renderers.

Key contents:
- Fixed-width-ish aliases: `UCHAR`, `USHORT`, `UINT`, `ULONG`.
- Platform-specific `diagram_type` for RISC OS Draw output versus portable file output.
- `output_type` linked-list fragment with text storage, width, font, color, and neighboring links.
- Conversion and encoding enums.
- Font table and user option structures.
- OLE PPS stream descriptors.
- Text/data/document/row/style/font/picture/section/header-footer/footnote/list block records.
- Image metadata, compression enums, row info enums, note type enums, and image info enums.

Research relevance:
- This header defines most cross-module data contracts used by property parsers, text block readers, and output backends.
