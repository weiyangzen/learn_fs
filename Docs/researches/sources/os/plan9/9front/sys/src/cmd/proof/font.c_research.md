# File Research: sources/os/plan9/9front/sys/src/cmd/proof/font.c

Font and character mapping support for the `proof` troff previewer. It reads a font map file, maps troff font names to bitmap font prefixes and character maps, lazily loads bitmap fonts/subfonts by size, and draws mapped characters on the screen.

Key behavior:
- `dochar` maps current rune/name through current font, special font, and optional fallback, then draws using `string`.
- `loadfont` searches `.font` files and subfont files under `libfont`, scaling troff size by magnification and map xheight.
- `readmapfile` parses `xheight`, `map`, `special`, and `troff` blocks.
- `buildmap` fills fast `quick` rune map for low values and linked-list map for compound/high names.
- `buildtroff` records troff-name to bitmap-prefix/map/fallback rows.
- `loadfontname` remaps a mounted font slot and frees cached fonts.

Integration points:
- Uses Plan 9 draw/event/font APIs.
- Called by `htroff.c` device-control font commands and character output.
- Shared globals declared in `proof.h`.

Risks:
- Fixed limits: `NMAP=5`, `NFONT`, `NSIZE`, `QUICK`, and static font map table size.
- `fontlookup` silently leaves previous/default state if a troff font is absent.
- Custom `log2` table is depth-specific and includes a noted “BUG” entry copied from libdraw.
