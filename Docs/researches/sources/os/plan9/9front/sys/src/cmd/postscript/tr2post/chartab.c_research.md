# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/chartab.c

Font and character mapping layer for `tr2post`. It maps troff mounted font names to troff font entries, reads troff metric files and PostScript font description files, builds glyph lookup tables, switches PostScript fonts, and emits document trailer font lists.

Key behavior:
- Maintains PostScript font name table (`pfnafontmtab`) and troff font table (`troffontab`).
- `mountfont` sets a troff font name at a mount position.
- `settrfont` resolves current troff mount position to a font table index.
- `setpsfont` emits PostScript font changes and optional slant/height transformations.
- `readpsfontdesc` reads `/sys/lib/postscript/troff/<font>` mapping ranges.
- `readtroffmetric` reads `/sys/lib/troff/font/dev<devname>/<font>` metrics and character mappings.
- `findtfn` lazily creates and loads font entries.

Integration points:
- Uses `Bgetfield`, `galloc`, global state from `tr2post.h`, and charcode output from common tables.
- `finish` reports only used PostScript fonts in the DSC trailer.

Risks:
- Several parser paths warn and continue on malformed font data, so downstream output may be partial.
- Quote-reuse support in troff metrics is marked “need some code here” and jumps to `flush`.
- Fixed path globals make font location assumptions explicit and not option-driven in this file.
