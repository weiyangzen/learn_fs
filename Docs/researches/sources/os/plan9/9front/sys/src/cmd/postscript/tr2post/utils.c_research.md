# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/utils.c

Positioning and glyph output utilities for `tr2post`. It tracks current horizontal/vertical position, font size/position, expected horizontal motion, resolves glyphs through current/special/fallback fonts, emits strings or build-character calls, and provides stubs for unimplemented helpers.

Key behavior:
- `hgoto`, `vgoto`, `hmot`, `vmot` update troff positions and flush strings when needed.
- `glyphout` resolves the current troff font, searches current and special fonts, falls back to a `pw` placeholder, maps to PostScript font ranges, and emits either string bytes or charlib build calls.
- `runeout` and `specialout` convert input to glyph tokens.
- `notavail` prints unavailable feature messages.

Integration points:
- Called by `conv.c`, `draw.c`, and font mapping code.
- Uses `charcode`, `troffontab`, `fontmtab`, `setpsfont`, `pageon`, `startstring`, `endstring`.

Risks:
- Some fallback paths use variables (`mi`) whose initialization depends on earlier special-character branches.
- `initialize`, `graphfunc`, and `nametorune` are stubs.
- Missing glyph fallback relies on finding `pw` in a special font.
