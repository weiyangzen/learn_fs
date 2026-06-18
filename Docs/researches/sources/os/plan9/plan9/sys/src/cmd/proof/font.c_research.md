# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/font.c

Purpose: Handles troff-to-bitmap font mapping and glyph rendering for the interactive `proof` viewer.

Key behavior:
- Maintains troff font names, loaded font cache by font/size, map selection, special font, and fontmap entries.
- `dochar` maps a rune/name to current font, special font, fallback font, or draws the name using the default screen font.
- `loadfont` searches configured bitmap font directory for `.font` or subfont files, with fallbacks.
- `loadfontname` remaps a troff font position and clears cached sizes.
- `readmapfile` parses map files with `xheight`, `map`, `special`, and `troff` sections.
- `buildmap` creates fast `quick` rune maps and linked-list slow maps.
- `buildtroff` maps troff names to bitmap filename prefixes and optional fallback fonts.
- `allfree` forces all font positions to dummy mappings.

Dependencies and integration:
- Uses Plan 9 draw/event/Bio APIs and `proof.h`.
- Called by `proof/main.c` and `proof/htroff.c`.

Risks and notes:
- Fixed maximums: `NMAP`, `NFONT`, `NSIZE`.
- Loading falls back through Times and Pelm paths.
- Missing fonts are fatal.
