# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/readDESC.c

Reads troff device `DESC` files for `tr2post`. It extracts printer description language, encoding, font mount table, device resolution, unit width, and ignores size/horizontal/vertical/special-character lists as needed.

Integration points:
- Called by `tr2post.c` before conversion.
- Uses `FONTDIR`, `devname`, `Bgetfield`, `mountfont`, and `findtfn`.
- Initializes globals `fontmnt`, `fontmtab`, `devres`, `unitwidth`, `printdesclang`, `encoding`.

Risks:
- State-machine parser depends on token ordering from DESC files.
- `descfilename` allocation length omits some separator/null slack but format string length likely over-allocates enough in practice.
- Special character list is ignored here; actual glyph availability depends on font metric loading.
