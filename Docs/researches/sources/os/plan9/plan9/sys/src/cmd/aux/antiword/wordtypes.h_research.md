# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordtypes.h

This header defines Antiword’s shared Word parsing and rendering data types.

Key contents:
- Basic unsigned integer typedefs.
- Platform-specific `diagram_type` for RISC OS drawfile/window output or generic `FILE *` output.
- Output fragments, conversion and encoding enums, options, font table entries, OLE PPS info, text/data blocks, document/row/style/font/picture/section/header/footer/note/list blocks, image metadata, row detection enum, note type enum, and image info enum.

Important details:
- `pps_info_type` is the OLE stream map used by Word 6+ parsing.
- `text_block_type` carries file offset, character position, length, Unicode flag, and property modifier.
- `style_block_type` is the central structure for paragraph/list rendering state.

Filesystem relevance:
- Indirect but foundational: models file offsets, stream positions, and parsed document structures.
