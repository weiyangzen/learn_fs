# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/utils.c

Purpose: Provides position tracking, horizontal/vertical motion, and glyph emission helpers for `tr2post`.

Key behavior:
- Tracks `hpos`, `vpos`, `fontsize`, and `fontpos`.
- `hgoto`, `vgoto`, `hmot`, and `vmot` update troff current position and flush strings as needed.
- `hmot` compares actual motion with expected glyph width and emits a space when motion matches current font’s space width.
- `findglyph` searches a font’s glyph linked list bucket.
- `glyphout` searches current font, special fonts, fallback font position 1, then Peter-face fallback `pw`; selects PostScript font and emits char strings or charlib build calls.
- Tracks required charlib definitions in `build_char_list`.
- `runeout` and `specialout` convert input to glyph lookup tokens.

Dependencies and integration:
- Core glyph layer used by `conv.c`.
- Depends on font tables from `chartab.c`, `pageon`, `startstring`, `endstring`, `charcode`, and PostScript font maps.

Risks and notes:
- Fallback behavior is warning-heavy and may silently substitute `pw`.
- Spacing logic depends on `expecthmot` matching later `hmot`.
- `nametorune` and `graphfunc` are stubs.
